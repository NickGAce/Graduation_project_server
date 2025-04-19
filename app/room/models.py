from sqlalchemy import Table, Column, Integer, String, ForeignKey

from app.database import metadata


# Таблица "Этажи"
floors = Table(
    "floors",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("floor_number", Integer)
)

# Таблица "Блоки"
blocks = Table(
    "blocks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("floor_id", Integer, ForeignKey("floors.id")),
    Column("block_name", String)
)

# Таблица "Комнаты"
rooms = Table(
    "rooms",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("block_id", Integer, ForeignKey("blocks.id")),
    Column("room_number", Integer),
    Column("max_capacity", Integer),
    Column("current_occupancy", Integer)
)
