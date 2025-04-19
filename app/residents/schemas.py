from datetime import date
from typing import Optional
from pydantic import BaseModel


# Схема для создания жителя
class ResidentCreate(BaseModel):
    user_id: Optional[int] = None
    full_name: str
    gender: str
    citizenship: str
    role: str
    faculty: Optional[str] = None
    group_number: Optional[str] = None
    date_of_check_in: date = date.today()
    date_of_check_out: Optional[date] = None
    room_id: Optional[int] = None
    email: str
    status: str


# Схема для обновления данных жителя
class ResidentUpdate(BaseModel):
    full_name: Optional[str] = None
    gender: Optional[str] = None
    citizenship: Optional[str] = None
    role: Optional[str] = None
    faculty: Optional[str] = None
    group_number: Optional[str] = None
    date_of_check_in: Optional[date] = None
    date_of_check_out: Optional[date] = None
    room_id: Optional[int] = None
    email: Optional[str] = None
    status: Optional[str] = None

