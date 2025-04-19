from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update, insert
from app.database import get_async_session
from app.room.models import blocks, rooms
from app.room.schemas import BlockCreate, BlockUpdate

router = APIRouter(
    prefix="/management/blocks",
    tags=["Management Blocks"]
)


@router.get("/blocks/{block_id}/rooms/")
async def get_blocks_by_floor_id(block_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(rooms).where(rooms.c.block_id == block_id).order_by(rooms.c.room_number)
    result = await session.execute(query)
    blocks_data = result.mappings().all()

    return {"status": "success", "data": blocks_data, "details": None}

# Получить все блоки, отсортированные по названию блока
@router.get("/blocks/")
async def get_all_blocks(session: AsyncSession = Depends(get_async_session)):
    query = select(blocks).order_by(blocks.c.block_name)
    result = await session.execute(query)
    return {"status": "success", "data": result.mappings().all(), "details": None}


# Получить блок по ID
@router.get("/blocks/{block_id}")
async def get_block_by_id(block_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(blocks).where(blocks.c.id == block_id))
    block_data = result.mappings().first()

    if not block_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")
    return {"status": "success", "data": block_data, "details": None}


# Создать новый блок
@router.post("/blocks/")
async def create_block(block_data: BlockCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(blocks).values(**block_data.dict()).returning(blocks)
    result = await session.execute(stmt)
    await session.commit()
    return {"status": "success", "message": "Block created successfully", "data": result.mappings().first()}


# Обновить блок
@router.patch("/blocks/{block_id}")
async def update_block(block_id: int, block_data: BlockUpdate, session: AsyncSession = Depends(get_async_session)):
    update_stmt = update(blocks).where(blocks.c.id == block_id).values(**block_data.dict(exclude_unset=True)).returning(blocks)
    result = await session.execute(update_stmt)
    await session.commit()
    updated_block = result.mappings().first()
    if not updated_block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")
    return {"status": "success", "message": "Block updated successfully", "data": updated_block}


# Удалить блок
@router.delete("/blocks/{block_id}")
async def delete_block(block_id: int, session: AsyncSession = Depends(get_async_session)):
    delete_stmt = delete(blocks).where(blocks.c.id == block_id)
    result = await session.execute(delete_stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")
    await session.commit()
    return {"status": "success", "message": "Block deleted successfully"}
