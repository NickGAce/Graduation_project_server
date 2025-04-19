from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, func
from app.database import get_async_session
from app.room.models import floors, rooms, blocks
from app.room.schemas import FloorCreate, FloorUpdate

router = APIRouter(
    prefix="/management/floors",
    tags=["Management Floors"]
)

@router.get("/floors/{floor_id}/blocks/")
async def get_blocks_by_floor_id(floor_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(blocks).where(blocks.c.floor_id == floor_id).order_by(blocks.c.block_name)
    result = await session.execute(query)
    blocks_data = result.mappings().all()

    return {"status": "success", "data": blocks_data, "details": None}


# Получение всех этажей, отсортировано по номеру этажа
@router.get("/floors/")
async def get_all_floors(session: AsyncSession = Depends(get_async_session)):
    query = select(floors).order_by(floors.c.floor_number)
    result = await session.execute(query)
    return {"status": "success", "data": result.mappings().all(), "details": None}


# Получение конкретного этажа по ID
@router.get("/floors/{floor_id}")
async def get_floor_by_id(floor_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(floors).where(floors.c.id == floor_id)
    result = await session.execute(query)
    floor_data = result.mappings().first()

    if not floor_data:
        raise HTTPException(status_code=404, detail="Этаж не найден")
    return {"status": "success", "data": floor_data, "details": None}


# Создание нового этажа
@router.post("/floors/")
async def create_floor(floor_data: FloorCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(floors).values(**floor_data.dict()).returning(floors)
    result = await session.execute(stmt)
    await session.commit()
    return {"status": "success", "data": result.mappings().first(), "details": None}


# Обновление данных этажа
@router.patch("/floors/{floor_id}")
async def update_floor(floor_id: int, floor_data: FloorUpdate, session: AsyncSession = Depends(get_async_session)):
    update_stmt = update(floors).where(floors.c.id == floor_id).values(**floor_data.dict(exclude_unset=True)).returning(floors)
    result = await session.execute(update_stmt)
    await session.commit()
    updated_floor = result.mappings().first()
    if not updated_floor:
        raise HTTPException(status_code=404, detail="Этаж не найден")
    return {"status": "success", "data": updated_floor, "details": None}


# Удаление этажа
@router.delete("/floors/{floor_id}")
async def delete_floor(floor_id: int, session: AsyncSession = Depends(get_async_session)):
    delete_stmt = delete(floors).where(floors.c.id == floor_id)
    result = await session.execute(delete_stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Этаж не найден")
    await session.commit()
    return {"status": "success", "message": "Этаж удален успешно"}

