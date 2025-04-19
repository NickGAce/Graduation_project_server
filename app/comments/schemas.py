from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Схема для создания комментария
class CommentCreate(BaseModel):
    room_id: int
    user_id: Optional[int] = None
    text: str


# Схема для обновления комментария
class CommentUpdate(BaseModel):
    text: Optional[str] = None
    updated_at: Optional[datetime] = datetime.now()


# Схема для чтения данных комментария
class CommentRead(BaseModel):
    id: int
    room_id: int
    user_id: int
    text: str
    created_at: datetime
    updated_at: datetime
