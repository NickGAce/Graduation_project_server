from sqlalchemy import Table, Column, Integer, String, Date, ForeignKey, Text, DateTime, func

from app.database import metadata

comments = Table(
    "comments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("room_id", Integer, ForeignKey("rooms.id"), nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),  # Предполагаем, что у вас есть таблица пользователей
    Column("text", Text, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())
)