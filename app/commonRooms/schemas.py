from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# Схема для создания общедоступной комнаты
class PublicRoomCreate(BaseModel):
    type_id: int
    room_name: str
    floor_id: int
    block_id: Optional[int] = None
    description: Optional[str] = None
    capacity: int


# Схема для обновления данных общедоступной комнаты
class PublicRoomUpdate(BaseModel):
    type_id: Optional[int] = None
    room_name: Optional[str] = None
    floor_id: Optional[int] = None
    block_id: Optional[int] = None
    description: Optional[str] = None
    capacity: Optional[int] = None


class BookingCreate(BaseModel):
    room_id: int
    user_id: int
    start_time: datetime
    end_time: datetime

class BookingUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool] = None