import uuid

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.users.exceptions import (
    CannotDeleteSelfError,
    CurrentPasswordIncorrectError,
    EmailAlreadyInUseError,
    EmailAlreadyRegisteredError,
    PasswordUnchangedError,
)
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate, UserUpdateMe
from app.users.selectors import get_user_by_email

DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


async def _ensure_email_available(
    *, session: AsyncSession, email: str, exclude_id: uuid.UUID
) -> None:
    """Guard the email-uniqueness invariant for updates.

    Raises EmailAlreadyInUseError if the email belongs to a different user.
    Single home for the rule shared by update_user and update_user_me.
    """
    existing = await get_user_by_email(session=session, email=email)
    if existing and existing.id != exclude_id:
        raise EmailAlreadyInUseError


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    existing = await get_user_by_email(session=session, email=user_create.email)
    if existing:
        raise EmailAlreadyRegisteredError
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def update_user(*, session: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    if user_data.get("email"):
        await _ensure_email_available(
            session=session, email=user_data["email"], exclude_id=db_user.id
        )
    extra_data = {}
    if "password" in user_data:
        extra_data["hashed_password"] = get_password_hash(user_data["password"])
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def update_user_me(
    *, session: AsyncSession, db_user: User, user_in: UserUpdateMe
) -> User:
    if user_in.email:
        await _ensure_email_available(
            session=session, email=user_in.email, exclude_id=db_user.id
        )
    user_data = user_in.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def change_password(
    *, session: AsyncSession, user: User, current_password: str, new_password: str
) -> None:
    """Change a user's password, enforcing the must-know-current / must-differ policy."""
    verified, _ = verify_password(current_password, user.hashed_password)
    if not verified:
        raise CurrentPasswordIncorrectError
    if current_password == new_password:
        raise PasswordUnchangedError
    await update_user(
        session=session, db_user=user, user_in=UserUpdate(password=new_password)
    )


async def delete_user(
    *, session: AsyncSession, db_user: User, acting_user: User
) -> None:
    """Delete a user on behalf of an admin; the actor may not delete themselves."""
    if db_user.id == acting_user.id:
        raise CannotDeleteSelfError
    await session.delete(db_user)
    await session.commit()


async def delete_own_account(*, session: AsyncSession, user: User) -> None:
    """Delete one's own account; superusers are not allowed to self-delete."""
    if user.is_superuser:
        raise CannotDeleteSelfError
    await session.delete(user)
    await session.commit()


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
