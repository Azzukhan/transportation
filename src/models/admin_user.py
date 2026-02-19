from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import AuditMixin, BaseModel, IDMixin

if TYPE_CHECKING:
    from src.models.admin_refresh_token import AdminRefreshToken
    from src.models.transport_company import TransportCompany


class AdminUser(IDMixin, AuditMixin, BaseModel):
    __tablename__ = "admin_users"

    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    transport_company_id: Mapped[int] = mapped_column(
        ForeignKey("transport_companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    transport_company: Mapped[TransportCompany] = relationship(back_populates="admin_users")
    refresh_tokens: Mapped[list[AdminRefreshToken]] = relationship(back_populates="admin_user")
