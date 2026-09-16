"""Alembic migration environment configuration.

The database URL is injected at runtime from the application settings module
so migrations always run against the same DATABASE_URL the application uses.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from src.shared.config import settings
from src.shared.infrastructure.database import Base

# Import ORM models so autogenerate can detect new tables.
from src.user.infrastructure.models import UserModel  # noqa: F401

# Alembic Config object, which provides access to alembic.ini values.
config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the logging configuration file.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata used by autogenerate support.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This generates the SQL script without a database connection.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the live database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
