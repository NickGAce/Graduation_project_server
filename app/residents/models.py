from sqlalchemy import Table, Column, Integer, String, Date, ForeignKey

from app.database import metadata

# Таблица "Жители"
residents = Table(
    "residents",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=True),  # Связь с таблицей пользователей
    Column("full_name", String(255), nullable=False),
    Column("gender", String(50), nullable=False),
    Column("citizenship", String(100), nullable=False),
    Column("role", String(100), nullable=False),
    Column("faculty", String(100), nullable=True),
    Column("group_number", String(50), nullable=True),  # Может быть пустым для сотрудников
    Column("date_of_check_in", Date, nullable=False),
    Column("date_of_check_out", Date),  # Может быть пустым, если житель все еще проживает
    Column("room_id", Integer, ForeignKey("rooms.id"), nullable=True),
    Column("email", String(255), nullable=False),
    Column("status", String(100), nullable=False)
)


