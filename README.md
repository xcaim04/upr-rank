# UPR-RANK

Juez en Línea (Online Judge) para la Universidad de Pinar del Río "Hermanos Saíz
Montes de Oca" (Cuba). Plataforma para la práctica y evaluación de problemas
algorítmicos, con soporte de concursos estilo ICPC/IOI, desarrollada como tesis de
grado en Ingeniería Informática.

*Dedicatoria: "En honor a Ali Landeiro Góngora"*

## Stack tecnológico

| Capa             | Tecnología                                                          |
| ---------------- | ------------------------------------------------------------------- |
| Backend Core     | Python 3.11, FastAPI, SQLAlchemy 2.0, PostgreSQL 15, Redis, JWT     |
| Judge Worker     | Python 3.11, Docker SDK (sandbox de contenedores efímeros), Redis   |
| Frontend Web     | React 18, Vite, TypeScript, TailwindCSS, React Query, Zustand       |
| Infraestructura  | Docker + Docker Compose                                             |
| Testing          | pytest + httpx (backend), Vitest + Testing Library (frontend)       |
| Calidad          | Ruff + Black (Python), ESLint + Prettier (TypeScript)               |

## Estructura del repositorio

```
upr-rank/
├── apps/
│   ├── backend_core/    # API REST (FastAPI). Screaming Architecture + Hexagonal
│   ├── judge_worker/    # Procesador de envíos (Redis + sandbox Docker)
│   └── frontend_web/    # Interfaz web (React + Vite + TypeScript)
├── packages/
│   └── shared-contracts/ # Contratos compartidos (tipos, DTOs, eventos)
├── docker-compose.yml
└── README.md
```

Cada módulo de dominio del backend sigue arquitectura hexagonal:

| Capa            | Responsabilidad                                            |
| --------------- | ---------------------------------------------------------- |
| `domain/`       | Entidades, Value Objects y reglas de negocio puras.        |
| `application/`  | Casos de uso (servicios) y puertos (interfaces).           |
| `infrastructure`| Adaptadores concretos (HTTP, repositorios, colas, etc.).   |

## Requisitos previos

- Docker + Docker Compose (para el entorno completo)
- Python 3.11+/uv y Node 20+ (solo para desarrollo local)

## Puesta en marcha con Docker Compose

1. Clona el repositorio:

   ```bash
   git clone https://github.com/xcaim04/upr-rank.git
   cd upr-rank
   ```

2. Levanta los servicios (PostgreSQL, Redis y backend):

   ```bash
   docker compose up --build
   ```

3. Verifica que el backend responde:

   ```bash
   curl http://localhost:8001/health
   # {"status":"ok","service":"upr-rank-backend"}
   ```

   Documentación interactiva de la API: http://localhost:8001/docs

### Endpoints de autenticación

```bash
# Registro de un alumno (devuelve par de tokens)
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"student@upr.edu.cu","username":"juanito","full_name":"Juan Pérez","password":"s3cret-pass"}'

# Login
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@upr.edu.cu","password":"s3cret-pass"}'

# Perfil del usuario autenticado
curl http://localhost:8001/auth/me \
  -H "Authorization: Bearer <access_token>"

# Refresh del access token
curl -X POST http://localhost:8001/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'

# Listado de usuarios (solo administradores)
curl http://localhost:8001/users \
  -H "Authorization: Bearer <access_token>"
```

## Desarrollo local

### Backend

```bash
cd apps/backend_core
uv venv                    # o: python -m venv .venv
uv pip install -r requirements.txt
cp ../../.env.example .env # ajusta DATABASE_URL/REDIS_URL si hace falta
alembic upgrade head
uvicorn src.main:app --reload
```

### Frontend

```bash
cd apps/frontend_web
npm install
npm run dev
```

### Calidad de código

```bash
# Backend
ruff check src tests
black --check src tests
pytest

# Frontend
npm run lint
npm run typecheck
```

## Convenciones

- **Commits** (Conventional Commits): `feat`, `fix`, `docs`, `style`, `refactor`,
  `test`, `chore`, `ci`, `perf` — un commit atómico por tarea lógica.
- **Idioma**: interfaz de usuario en español; código fuente y mensajes de commit
  en inglés.
- **Arquitectura**: lógica de negocio solo en `domain/`; nunca importar SQLAlchemy
  ni FastAPI dentro de la capa de dominio.
- **Configuración**: siempre mediante variables de entorno, nunca secretos
  hardcodeados.

## Estado del proyecto

El desarrollo avanza por sprints (ver `docs/roadmap.md`). Cada sprint entrega una
funcionalidad completa y verificable.

**Sprint 0 — Fundación: completo.** Monorepo con `apps/backend_core`,
`apps/judge_worker`, `apps/frontend_web` y `packages/shared-contracts`; FastAPI
con endpoint `/health`; SQLAlchemy conectado a PostgreSQL; Alembic configurado
(se aplican migraciones en el arranque del contenedor); `docker compose up`
levanta PostgreSQL + Redis + backend.

**Sprint 1 — Autenticación y usuarios: completo.** Registro, login, refresh y
perfil (`/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/me`) con
contraseñas bcrypt y tokens JWT (access + refresh); RBAC por roles
(alumno/profesor/admin); listado de usuarios restringido (`GET /users`, solo
admin). Migración de la tabla `users` incluida. Próximo: Sprint 2 (gestión de
problemas).