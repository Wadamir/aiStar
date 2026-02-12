from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.base import Base

if TYPE_CHECKING:
    from bot.db.models.user import User


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=False,  # important for seeding predefined plans
    )

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    daily_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    price_stars: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    users: Mapped[list["User"]] = relationship(
        back_populates="plan",
    )