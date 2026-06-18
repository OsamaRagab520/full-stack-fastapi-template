# Full Stack FastAPI Template

A production-ready full-stack web application template built with FastAPI, React, and PostgreSQL. Includes authentication, email, database migrations, end-to-end testing, and Docker-based deployment out of the box.

## Technology Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com) — high-performance Python API framework
- [SQLModel](https://sqlmodel.tiangolo.com) — SQL ORM built on SQLAlchemy and Pydantic
- [Pydantic](https://docs.pydantic.dev) — data validation and settings management
- [PostgreSQL](https://www.postgresql.org) — relational database
- [Alembic](https://alembic.sqlalchemy.org) — database migrations
- [Pytest](https://pytest.org) — backend testing

**Frontend**
- [React](https://react.dev) + [TypeScript](https://www.typescriptlang.org) — UI framework
- [Vite](https://vitejs.dev) — build tool and dev server
- [TanStack Query](https://tanstack.com/query) + [TanStack Router](https://tanstack.com/router) — data fetching and routing
- [Tailwind CSS](https://tailwindcss.com) + [shadcn/ui](https://ui.shadcn.com) — styling and components
- [Playwright](https://playwright.dev) — end-to-end testing
- Auto-generated API client from OpenAPI schema

**Infrastructure**
- [Docker Compose](https://www.docker.com) — local development and production
- [Traefik](https://traefik.io) — reverse proxy with automatic HTTPS
- [Mailcatcher](https://mailcatcher.me) — local email testing
- GitHub Actions — CI/CD

**Security**
- JWT (JSON Web Token) authentication
- Secure password hashing (bcrypt)
- Email-based password recovery

## Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Bun](https://bun.sh/) (JavaScript runtime and package manager)

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url> my-project
cd my-project
```

### 2. Configure environment variables

Copy the example env file and update it with your values:

```bash
cp .env.example .env
```

At minimum, change the following before any deployment:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Application secret key |
| `FIRST_SUPERUSER_PASSWORD` | Initial admin password |
| `POSTGRES_PASSWORD` | Database password |

Generate secure random values with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Start the development stack

```bash
docker compose watch
```

The services will be available at:

| Service | URL |
|---|---|
| API | http://localhost/api/v1 |
| API docs (Swagger) | http://localhost/docs |
| Frontend | http://localhost:5173 |
| Mailcatcher | http://localhost:1080 |

## Project Structure

```
.
├── backend/            # FastAPI application
│   ├── app/
│   │   ├── api/        # Route definitions
│   │   ├── auth/       # Authentication logic
│   │   ├── core/       # Config, database, security
│   │   ├── emails/     # Email sending utilities
│   │   ├── items/      # Example domain module
│   │   ├── users/      # User domain module
│   │   ├── models.py   # SQLModel table definitions
│   │   └── main.py     # Application entrypoint
│   └── alembic/        # Database migrations
├── frontend/           # React application
│   └── src/
│       ├── client/     # Auto-generated API client
│       ├── components/ # Shared UI components
│       ├── hooks/      # Custom React hooks
│       └── routes/     # Page components
├── scripts/            # Dev and CI utility scripts
├── compose.yml         # Production Compose config
└── compose.override.yml # Local development overrides
```

## Development

Detailed development guides:

- [Backend development](./backend/README.md) — Python environment, migrations, testing
- [Frontend development](./frontend/README.md) — local dev server, client generation, E2E tests
- [Local development setup](./development.md) — Docker Compose, custom domains, env config

## Deployment

See [deployment.md](./deployment.md) for full instructions, including:

- Docker Compose production configuration
- Traefik setup with automatic TLS certificates
- Environment-specific configuration

## Using a Private Repository

GitHub does not allow changing fork visibility. To use this as a private repository:

```bash
# Clone into a new directory
git clone <this-repo-url> my-project
cd my-project

# Point origin to your private repo
git remote set-url origin git@github.com:<you>/my-project.git

# Keep upstream as a reference for future updates
git remote add upstream <this-repo-url>

# Push to your private repo
git push -u origin master
```

To pull future upstream updates:

```bash
git pull --no-commit upstream master
# Resolve any conflicts, then:
git merge --continue
```

## Release Notes

See [release-notes.md](./release-notes.md).

## License

Licensed under the [MIT License](./LICENSE).
