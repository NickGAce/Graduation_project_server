from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, insert
from app.database import get_async_session
from app.ratings.models import residents_ratings
from app.residents.models import residents
from app.residents.schemas import ResidentCreate, ResidentUpdate

router = APIRouter(
    prefix="/management/residents",
    tags=["Management Residents"]
)


@router.get("/residents/no-room")
async def get_residents_without_rooms(session: AsyncSession = Depends(get_async_session)):
    # Формируем SQL запрос для поиска всех записей, где room_id равно null
    query = select(residents).where(residents.c.room_id == None)
    result = await session.execute(query)
    residents_data = result.mappings().all()

    if not residents_data:
        return {"status": "error", "message": "No residents found without a room", "data": []}

    # Возвращаем данные в формате, который уже используется в вашем API
    return {"status": "success", "data": residents_data}


# Получение всех жителей
@router.get("/residents/")
async def get_all_residents(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(residents).order_by(residents.c.id))
    return {"status": "success", "data": result.mappings().all(), "details": None}

# Получение жителя по ID
@router.get("/residents/{resident_id}")
async def get_resident_by_id(resident_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(residents).where(residents.c.id == resident_id))
    resident_data = result.mappings().first()

    if not resident_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")
    return {"status": "success", "data": resident_data, "details": None}

# Создание нового жителя
@router.post("/residents/")
async def create_resident(resident_data: ResidentCreate, session: AsyncSession = Depends(get_async_session)):
    # Создание записи жителя
    stmt = insert(residents).values(**resident_data.dict()).returning(residents)
    result = await session.execute(stmt)
    new_resident = result.mappings().first()
    await session.commit()

    # Начальные значения рейтинга
    initial_achievement_score = 0.0
    initial_infraction_score = 0.0
    initial_overall_score = 3.0  # Начальный overall_score может быть установлен в среднее значение

    # Создание записи рейтинга для нового жителя
    rating_stmt = insert(residents_ratings).values(
        resident_id=new_resident['id'],
        achievement_score=initial_achievement_score,
        infraction_score=initial_infraction_score,
        overall_score=initial_overall_score
    )
    await session.execute(rating_stmt)
    await session.commit()

    return {
        "status": "success",
        "message": "Resident and initial rating created successfully",
        "data": new_resident
    }

# Обновление данных жителя
@router.patch("/residents/{resident_id}")
async def update_resident(resident_id: int, resident_data: ResidentUpdate, session: AsyncSession = Depends(get_async_session)):
    update_stmt = update(residents).where(residents.c.id == resident_id).values(**resident_data.dict(exclude_unset=True)).returning(residents)
    result = await session.execute(update_stmt)
    await session.commit()
    updated_resident = result.mappings().first()
    if not updated_resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")
    return {"status": "success", "message": "Resident updated successfully", "data": updated_resident}

# Удаление жителя
@router.delete("/residents/{resident_id}")
async def delete_resident(resident_id: int, session: AsyncSession = Depends(get_async_session)):
    # Удаление связанных рейтингов
    await session.execute(delete(residents_ratings).where(residents_ratings.c.resident_id == resident_id))

    # Удаление жителя
    delete_stmt = delete(residents).where(residents.c.id == resident_id)
    result = await session.execute(delete_stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

    await session.commit()
    return {"status": "success", "message": "Resident and related ratings deleted successfully"}

