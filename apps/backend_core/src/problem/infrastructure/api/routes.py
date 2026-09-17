"""Problem management API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, Security
from sqlalchemy.orm import Session
from src.auth.application.errors import ForbiddenError
from src.auth.infrastructure.api.authorization import require_roles
from src.auth.infrastructure.api.dependencies import get_current_user
from src.problem.application.dtos import CreateProblemInput, UpdateProblemInput
from src.problem.application.errors import ProblemNotFoundError
from src.problem.application.use_cases import (
    CreateProblem,
    DeleteProblem,
    GetProblem,
    ListProblems,
    UpdateProblem,
)
from src.problem.infrastructure.api.schemas import ProblemOut
from src.problem.infrastructure.repository import SQLAlchemyProblemRepository
from src.shared.infrastructure.database import get_db
from src.user.domain.entities import Role, User

router = APIRouter(prefix="/problems", tags=["problems"])


@router.post(
    "",
    response_model=ProblemOut,
    status_code=201,
    summary="Create a problem (teacher or admin)",
    description="Creates a problem and returns it. Teachers can manage their own "
    "problems; admins can manage all of them.",
    responses={403: {"description": "The caller role lacks permission"}},
)
def create_problem(
    data: CreateProblemInput,
    current_user: User = Security(require_roles(Role.TEACHER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> ProblemOut:
    problems = SQLAlchemyProblemRepository(db)
    problem = CreateProblem(problems).execute(data, author_id=current_user.id)
    db.commit()
    return ProblemOut.from_domain(problem)


@router.get(
    "",
    response_model=list[ProblemOut],
    summary="List problems",
    description="Returns problems ordered by creation. Students only see published "
    "problems; teachers and admins see all of them.",
    responses={401: {"description": "Missing, invalid or expired token"}},
)
def list_problems(
    offset: int = 0,
    limit: int = 50,
    current_user: User = Security(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProblemOut]:
    visible_only = current_user.role is Role.STUDENT
    problems = ListProblems(SQLAlchemyProblemRepository(db)).execute(
        visible_only=visible_only, offset=offset, limit=limit
    )
    return [ProblemOut.from_domain(problem) for problem in problems]


@router.get(
    "/{problem_id}",
    response_model=ProblemOut,
    summary="Get a problem",
    description="Returns a single problem. Students cannot see unpublished problems.",
    responses={
        401: {"description": "Missing, invalid or expired token"},
        404: {"description": "Problem not found or hidden for the caller"},
    },
)
def get_problem(
    problem_id: UUID,
    current_user: User = Security(get_current_user),
    db: Session = Depends(get_db),
) -> ProblemOut:
    problem = GetProblem(SQLAlchemyProblemRepository(db)).execute(problem_id)
    if current_user.role is Role.STUDENT and not problem.is_visible:
        raise ProblemNotFoundError()
    return ProblemOut.from_domain(problem)


@router.patch(
    "/{problem_id}",
    response_model=ProblemOut,
    summary="Update a problem (teacher or admin)",
    description="Applies a partial update. Teachers can only edit their own "
    "problems; admins can edit any problem.",
    responses={
        403: {"description": "The caller lacks permission"},
        404: {"description": "Problem not found"},
    },
)
def update_problem(
    problem_id: UUID,
    data: UpdateProblemInput,
    current_user: User = Security(require_roles(Role.TEACHER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> ProblemOut:
    problems = SQLAlchemyProblemRepository(db)
    problem = GetProblem(problems).execute(problem_id)
    if problem.author_id != current_user.id and current_user.role is not Role.ADMIN:
        raise ForbiddenError()
    updated = UpdateProblem(problems).execute(problem_id, data)
    db.commit()
    return ProblemOut.from_domain(updated)


@router.delete(
    "/{problem_id}",
    status_code=204,
    summary="Delete a problem (admin only)",
    description="Permanently removes a problem. Restricted to administrators.",
    responses={404: {"description": "Problem not found"}},
)
def delete_problem(
    problem_id: UUID,
    _: User = Security(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db),
) -> Response:
    DeleteProblem(SQLAlchemyProblemRepository(db)).execute(problem_id)
    db.commit()
    return Response(status_code=204)
