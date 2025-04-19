from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update, insert
from app.database import get_async_session
from app.room.models import rooms, blocks, floors
from app.room.schemas import RoomCreate, RoomUpdate

router = APIRouter(
    prefix="/management/rooms",
    tags=["Management Rooms"]
)


# Получение всех комнат с информацией о блоке и этаже, отсортировано по номеру комнаты
@router.get("/rooms/")
async def get_all_rooms(session: AsyncSession = Depends(get_async_session)):
    stmt = select(
        rooms.c.id,
        rooms.c.room_number,
        rooms.c.max_capacity,
        rooms.c.current_occupancy,
        blocks.c.block_name,
        floors.c.floor_number
    ).select_from(
        rooms.join(blocks).join(floors)
    ).order_by(rooms.c.room_number)
    result = await session.execute(stmt)
    rooms_data = result.fetchall()
    return {"status": "success", "data": [
        {
            "id": room.id,
            "room_number": room.room_number,
            "max_capacity": room.max_capacity,
            "current_occupancy": room.current_occupancy,
            "block_name": room.block_name,
            "floor_number": room.floor_number
        } for room in rooms_data
    ], "details": None}


# Получение комнаты по ID с информацией о блоке и этаже, отсортировано по номеру комнаты
@router.get("/rooms/{room_id}")
async def get_room_by_id(room_id: int, session: AsyncSession = Depends(get_async_session)):
    stmt = select(
        rooms.c.id,
        rooms.c.room_number,
        rooms.c.max_capacity,
        rooms.c.current_occupancy,
        blocks.c.block_name,
        floors.c.floor_number
    ).select_from(
        rooms.join(blocks).join(floors)
    ).where(rooms.c.id == room_id).order_by(rooms.c.room_number)
    result = await session.execute(stmt)
    room_data = result.fetchone()
    if not room_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return {"status": "success", "data": {
        "id": room_data.id,
        "room_number": room_data.room_number,
        "max_capacity": room_data.max_capacity,
        "current_occupancy": room_data.current_occupancy,
        "block_name": room_data.block_name,
        "floor_number": room_data.floor_number
    }, "details": None}

# Создание новой комнаты
@router.post("/rooms/")
async def create_room(room_data: RoomCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(rooms).values(**room_data.dict()).returning(rooms)
    result = await session.execute(stmt)
    await session.commit()
    return {"status": "success", "message": "Room created successfully", "data": result.mappings().first()}


# Обновление данных комнаты
@router.patch("/rooms/{room_id}")
async def update_room(room_id: int, room_data: RoomUpdate, session: AsyncSession = Depends(get_async_session)):
    update_stmt = update(rooms).where(rooms.c.id == room_id).values(**room_data.dict(exclude_unset=True)).returning(rooms)
    result = await session.execute(update_stmt)
    await session.commit()
    updated_room = result.mappings().first()
    if not updated_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return {"status": "success", "message": "Room updated successfully", "data": updated_room}


# Удаление комнаты
@router.delete("/rooms/{room_id}")
async def delete_room(room_id: int, session: AsyncSession = Depends(get_async_session)):
    delete_stmt = delete(rooms).where(rooms.c.id == room_id)
    result = await session.execute(delete_stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    await session.commit()
    return {"status": "success", "message": "Room deleted successfully"}
