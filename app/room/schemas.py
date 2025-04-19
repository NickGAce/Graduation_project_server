from typing import Optional
from pydantic import BaseModel


# Схемы для этажей
class FloorCreate(BaseModel):
    floor_number: int


class FloorUpdate(BaseModel):
    floor_number: Optional[int] = None


# Схемы для блоков
class BlockCreate(BaseModel):
    floor_id: int
    block_name: str


class BlockUpdate(BaseModel):
    floor_id: Optional[int] = None
    block_name: Optional[str] = None


# Схемы для комнат
class RoomCreate(BaseModel):
    block_id: int
    room_number: int
    max_capacity: int
    current_occupancy: int


class RoomUpdate(BaseModel):
    block_id: Optional[int] = None
    room_number: Optional[int] = None
    max_capacity: Optional[int] = None
    current_occupancy: Optional[int] = None
