"""Data-access layer for the User model.

Contains every database query related to users. Services call these
methods rather than issuing SQLAlchemy queries themselves, keeping
persistence concerns isolated from business logic.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


class UserRepository:
    """Encapsulates all database access for the User model."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Fetch a user by primary key, or None if no such user exists."""
        return await self._db.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email address, or None if no such user exists."""
        result = await self._db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Check whether a user with the given email already exists."""
        result = await self._db.execute(
            select(func.count()).select_from(User).where(User.email == email)
        )
        return (result.scalar_one() or 0) > 0

    async def create(self, user: User) -> User:
        """Persist a new user and return it with database-generated fields populated."""
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """Persist changes made to an already-tracked user instance."""
        await self._db.commit()
        await self._db.refresh(user)
        return user

    async def set_refresh_token_hash(
        self, user_id: UUID, refresh_token_hash: str | None
    ) -> None:
        """Store (or clear, if None) the hashed refresh token for a user."""
        user = await self.get_by_id(user_id)
        if user is not None:
            user.refresh_token_hash = refresh_token_hash
            await self._db.commit()

    async def count_total(self) -> int:
        """Return the total number of registered users."""
        result = await self._db.execute(select(func.count()).select_from(User))
        return result.scalar_one() or 0

    async def count_by_role(self, role: UserRole) -> int:
        """Return the number of users with a specific role."""
        result = await self._db.execute(
            select(func.count()).select_from(User).where(User.role == role)
        )
        return result.scalar_one() or 0