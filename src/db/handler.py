"""Compatibility shim. Prefer importing from src.db.db_handler."""

from src.db.db_handler import GenericDBHandler

__all__ = ["GenericDBHandler"]
