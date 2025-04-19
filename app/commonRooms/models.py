from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, Boolean, func

from app.database import metadata

# Таблица "Типы общедоступных комнат"
room_types = Table(
    "room_types",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("type_name", String, nullable=False),
    Column("description", String)
)

# Обновленная таблица "Общедоступные комнаты"
public_rooms = Table(
    "public_rooms",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("type_id", Integer, ForeignKey("room_types.id")),
    Column("room_name", String, nullable=False),
    Column("floor_id", Integer, ForeignKey("floors.id")),  # Связь с таблицей этажей
    Column("block_id", Integer, ForeignKey("blocks.id"), nullable=True),  # Необязательное поле
    Column("description", String),
    Column("capacity", Integer)
)

# Таблица "Бронирования комнат досуга"
room_bookings = Table(
    "room_bookings",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("room_id", Integer, ForeignKey("public_rooms.id")),
    Column("user_id", Integer, ForeignKey("user.id")),  # Предполагается, что есть таблица пользователей
    Column("start_time", DateTime, nullable=False),
    Column("end_time", DateTime, nullable=False),
    Column("is_active", Boolean, default=True),  # Индикатор активного бронирования
    Column("created_at", DateTime, server_default=func.now())
)
