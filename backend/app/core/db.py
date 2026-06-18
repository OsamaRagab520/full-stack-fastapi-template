from sqlmodel import Session, create_engine, select

from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    # Importing here ensures all table models are registered with SQLAlchemy's
    # mapper before the first query runs. See:
    # https://github.com/fastapi/full-stack-fastapi-template/issues/28
    from app.items.models import Item  # noqa: F401
    from app.users import service as users_service
    from app.users.models import User
    from app.users.schemas import UserCreate

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        users_service.create_user(session=session, user_create=user_in)
