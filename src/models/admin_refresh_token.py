from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import AuditMixin, BaseModel, IDMixin

if TYPE_CHECKING:
    from src.models.admin_user import AdminUser


class AdminRefreshToken(IDMixin, AuditMixin, BaseModel):
    __tablename__ = "admin_refresh_tokens"

    admin_user_id: Mapped[int] = mapped_column(
        ForeignKey("admin_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    family_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    replaced_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("admin_refresh_tokens.id", ondelete="SET NULL"),
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    admin_user: Mapped[AdminUser] = relationship(back_populates="refresh_tokens")
