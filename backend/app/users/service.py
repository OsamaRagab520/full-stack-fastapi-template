from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate, UserUpdateMe

DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    existing = await get_user_by_email(session=session, email=user_create.email)
    if existing:
        raise ValueError("email_already_registered")
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def update_user(*, session: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    if "email" in user_data and user_data["email"]:
        existing = await get_user_by_email(session=session, email=user_data["email"])
        if existing and existing.id != db_user.id:
            raise ValueError("email_already_in_use")
    extra_data = {}
    if "password" in user_data:
        extra_data["hashed_password"] = get_password_hash(user_data["password"])
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def update_user_data(
    *, session: AsyncSession, db_user: User, user_in: UserUpdateMe
) -> User:
    if user_in.email:
        existing = await get_user_by_email(session=session, email=user_in.email)
        if existing and existing.id != db_user.id:
            raise ValueError("email_already_in_use")
    user_data = user_in.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def delete_user(*, session: AsyncSession, db_user: User) -> None:
    await session.delete(db_user)
    await session.commit()


async def get_user_by_email(*, session: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return (await session.exec(statement)).first()


async def authenticate(*, session: AsyncSession, email: str, password: str) -> User | None:
    db_user = await get_user_by_email(session=session, email=email)
    if not db_user:
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
    return db_user


async def update_user_password(
    *, session: AsyncSession, db_user: User, new_password: str
) -> None:
    db_user.hashed_password = get_password_hash(new_password)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
