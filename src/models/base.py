from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class BaseModel(Base):
    __abstract__ = True


class IDMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class CompanyMixin:
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )


class TransportCompanyMixin:
    transport_company_id: Mapped[int] = mapped_column(
        ForeignKey("transport_companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
