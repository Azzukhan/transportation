from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_subject
from src.core.config import Settings, get_settings
from src.db.session import get_db_session

SettingsDep = Annotated[Settings, Depends(get_settings)]
DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
CurrentSubjectDep = Annotated[str, Depends(get_current_subject)]
