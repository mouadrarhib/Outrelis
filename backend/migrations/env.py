from alembic import context
from sqlalchemy import create_engine, pool

from app.config import get_settings
from app.db import Base
from app.features.auth import models  # noqa: F401
from app.features.discovery import models as discovery_models  # noqa: F401
from app.features.onboarding import models as onboarding_models  # noqa: F401
from app.features.prospecting import models as prospecting_models  # noqa: F401

config = context.config


def configure(connection):
    context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(
        url=get_settings().database_url.get_secret_value(),
        target_metadata=Base.metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()
elif config.attributes.get("connection") is not None:
    configure(config.attributes["connection"])
else:
    engine = create_engine(
        get_settings().database_url.get_secret_value(), poolclass=pool.NullPool,
        hide_parameters=True,
    )
    with engine.connect() as connection:
        configure(connection)
