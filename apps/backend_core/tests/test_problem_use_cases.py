"""Unit tests for the problem use cases."""

from uuid import UUID

import pytest
from src.problem.application.dtos import CreateProblemInput, UpdateProblemInput
from src.problem.application.errors import ProblemNotFoundError, SlugAlreadyExistsError
from src.problem.application.ports import ProblemRepository
from src.problem.application.use_cases import (
    CreateProblem,
    DeleteProblem,
    GetProblem,
    ListProblems,
    UpdateProblem,
)
from src.problem.domain.entities import Difficulty, Problem

pytestmark = pytest.mark.unit

AUTHOR_ID = UUID("11111111-1111-4111-8111-111111111111")


class FakeProblemRepository(ProblemRepository):
    """In-memory double of the problem persistence port."""

    def __init__(self) -> None:
        self._problems: list[Problem] = []
        self._next_id = 0

    def add(self, problem: Problem) -> None:
        problem.id = UUID(int=self._next_id + 1)
        self._next_id += 1
        self._problems.append(problem)

    def get_by_id(self, problem_id: UUID) -> Problem | None:
        return next((p for p in self._problems if p.id == problem_id), None)

    def get_by_slug(self, slug: str) -> Problem | None:
        return next((p for p in self._problems if p.slug == slug), None)

    def list(
        self, *, visible_only: bool, offset: int = 0, limit: int = 50
    ) -> list[Problem]:
        problems = [p for p in self._problems if not visible_only or p.is_visible]
        return problems[offset : offset + limit]

    def update(self, problem: Problem) -> None:
        for index, stored in enumerate(self._problems):
            if stored.id == problem.id:
                self._problems[index] = problem
                return
        self._problems.append(problem)

    def delete(self, problem_id: UUID) -> None:
        self._problems = [p for p in self._problems if p.id != problem_id]


@pytest.fixture()
def repository() -> FakeProblemRepository:
    return FakeProblemRepository()


def _input(**overrides: object) -> CreateProblemInput:
    defaults: dict[str, object] = {
        "title": "Suma de dos números",
        "statement": "Dados dos enteros, calcula su suma.",
        "difficulty": Difficulty.EASY,
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
    }
    defaults.update(overrides)
    return CreateProblemInput(**defaults)


def _seed(repository: FakeProblemRepository, **overrides: object) -> Problem:
    return CreateProblem(repository).execute(_input(**overrides), author_id=AUTHOR_ID)


def test_creates_problem_with_derived_slug(
    repository: FakeProblemRepository,
) -> None:
    problem = _seed(repository)

    assert problem.title == "Suma de dos números"
    assert problem.slug == "suma-de-dos-numeros"
    assert problem.difficulty is Difficulty.EASY
    assert problem.author_id == AUTHOR_ID
    assert problem.is_visible is False

    other = CreateProblem(repository).execute(
        _input(title="Árbol binario"), author_id=AUTHOR_ID
    )

    assert len(repository._problems) == 2
    assert other.slug == "arbol-binario"


def test_creates_problem_with_explicit_slug(
    repository: FakeProblemRepository,
) -> None:
    problem = CreateProblem(repository).execute(
        _input(slug="suma-2026"), author_id=AUTHOR_ID
    )

    assert problem.slug == "suma-2026"


def test_normalizes_explicit_slug(repository: FakeProblemRepository) -> None:
    problem = CreateProblem(repository).execute(
        _input(slug="  Suma-2026  "), author_id=AUTHOR_ID
    )

    assert problem.slug == "suma-2026"


def test_rejects_duplicate_slug(repository: FakeProblemRepository) -> None:
    _seed(repository)

    with pytest.raises(SlugAlreadyExistsError):
        CreateProblem(repository).execute(
            _input(title="Otro título", slug="suma-de-dos-numeros"),
            author_id=AUTHOR_ID,
        )


def test_get_problem_by_id(repository: FakeProblemRepository) -> None:
    created = _seed(repository)

    problem = GetProblem(repository).execute(created.id)

    assert problem.id == created.id
    assert problem.title == created.title


def test_get_missing_problem_raises(repository: FakeProblemRepository) -> None:
    with pytest.raises(ProblemNotFoundError):
        GetProblem(repository).execute(UUID("99999999-9999-4999-8999-999999999999"))


def test_list_problems_to_public_audience(
    repository: FakeProblemRepository,
) -> None:
    _seed(repository)
    CreateProblem(repository).execute(
        _input(title="Problema oculto", is_visible=False), author_id=AUTHOR_ID
    )
    CreateProblem(repository).execute(
        _input(title="Problema público", is_visible=True), author_id=AUTHOR_ID
    )

    public = ListProblems(repository).execute(visible_only=True)

    assert len(public) == 1
    assert public[0].title == "Problema público"


def test_list_problems_to_staff_shows_all(
    repository: FakeProblemRepository,
) -> None:
    _seed(repository)
    CreateProblem(repository).execute(
        _input(title="Problema oculto", is_visible=False), author_id=AUTHOR_ID
    )

    all_problems = ListProblems(repository).execute(visible_only=False)

    assert len(all_problems) == 2


def test_list_problems_respects_pagination(repository: FakeProblemRepository) -> None:
    for index in range(5):
        _seed(repository, title=f"Problema {index}")

    page = ListProblems(repository).execute(visible_only=False, offset=1, limit=2)

    assert len(page) == 2
    assert page[0].title == "Problema 1"


def test_update_problem_fields(repository: FakeProblemRepository) -> None:
    created = _seed(repository)

    updated = UpdateProblem(repository).execute(
        created.id,
        UpdateProblemInput(title="Suma avanzada", is_visible=True),
    )

    assert updated.title == "Suma avanzada"
    assert updated.is_visible is True
    assert updated.slug == "suma-de-dos-numeros"
    repo_problem = repository.get_by_id(created.id)
    assert repo_problem is not None
    assert repo_problem.title == "Suma avanzada"


def test_update_problem_slug_conflict(repository: FakeProblemRepository) -> None:
    _seed(repository, title="Primero", slug="primero")
    second = _seed(repository, title="Segundo", slug="segundo")

    with pytest.raises(SlugAlreadyExistsError):
        UpdateProblem(repository).execute(second.id, UpdateProblemInput(slug="primero"))


def test_update_missing_problem_raises(repository: FakeProblemRepository) -> None:
    with pytest.raises(ProblemNotFoundError):
        UpdateProblem(repository).execute(
            UUID("99999999-9999-4999-8999-999999999999"), UpdateProblemInput()
        )


def test_delete_problem(repository: FakeProblemRepository) -> None:
    created = _seed(repository)

    DeleteProblem(repository).execute(created.id)

    assert repository.get_by_id(created.id) is None


def test_delete_missing_problem_raises(repository: FakeProblemRepository) -> None:
    with pytest.raises(ProblemNotFoundError):
        DeleteProblem(repository).execute(UUID("99999999-9999-4999-8999-999999999999"))
