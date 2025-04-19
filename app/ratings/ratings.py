from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.database import get_async_session
from app.ratings.models import residents_ratings
from app.ratings.schemas import RatingCreate, RatingUpdate


ACHIEVEMENT_INCREMENTS = {
    'small': 0.1,
    'medium': 0.5,
    'large': 1.0
}

INFRACTION_DECREMENTS = {
    'minor': 0.1,
    'moderate': 0.5,
    'major': 1.0
}


router = APIRouter(
    prefix="/management/ratings",
    tags=["Management Ratings"]
)

# Получение всех рейтингов
@router.get("/ratings/")
async def get_all_ratings(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(residents_ratings))
    return {"status": "success", "data": result.mappings().all()}


# Получение рейтинга по ID жителя
@router.get("/ratings/{resident_id}")
async def get_rating_by_resident(resident_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(residents_ratings).where(residents_ratings.c.resident_id == resident_id))
    rating = result.mappings().first()
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    return {"status": "success", "data": rating}


# Создание нового рейтинга
@router.post("/ratings/")
async def create_rating(rating_data: RatingCreate, session: AsyncSession = Depends(get_async_session)):
    overall_score = rating_data.achievement_score - rating_data.infraction_score
    stmt = insert(residents_ratings).values(
        resident_id=rating_data.resident_id,
        achievement_score=rating_data.achievement_score,
        infraction_score=rating_data.infraction_score,
        overall_score=overall_score
    )
    result = await session.execute(stmt)
    await session.commit()

    return {"status": "success", "message": "Rating created successfully"}


# Удаление рейтинга
@router.delete("/ratings/{rating_id}")
async def delete_rating(rating_id: int, session: AsyncSession = Depends(get_async_session)):
    delete_stmt = delete(residents_ratings).where(residents_ratings.c.id == rating_id)
    result = await session.execute(delete_stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    await session.commit()
    return {"status": "success", "message": "Rating deleted successfully"}


@router.patch("/ratings/{rating_id}/increase_achievement/{change_type}")
async def increase_achievement(rating_id: int, change_type: str, session: AsyncSession = Depends(get_async_session)):
    increment = ACHIEVEMENT_INCREMENTS.get(change_type)
    if not increment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid change type specified")

    async with session.begin():
        current_data = await session.execute(select(residents_ratings).where(residents_ratings.c.id == rating_id))
        current_rating = current_data.mappings().first()

        if not current_rating:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")

        # Получаем изначальный рейтинг
        initial_overall_score = current_rating['overall_score']

        # Увеличиваем achievement_score
        new_achievement_score = current_rating['achievement_score'] + increment

        # Пересчитываем общий рейтинг с учетом изначального значения
        new_overall_score = max(1, min(5, initial_overall_score + increment))

        await session.execute(
            update(residents_ratings).where(residents_ratings.c.id == rating_id).values(
                achievement_score=new_achievement_score,
                overall_score=new_overall_score
            )
        )

    return {"status": "success", "message": "Achievement score increased successfully"}


@router.patch("/ratings/{rating_id}/decrease_infraction/{change_type}")
async def decrease_infraction(rating_id: int, change_type: str, session: AsyncSession = Depends(get_async_session)):
    decrement = INFRACTION_DECREMENTS.get(change_type)
    if not decrement:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid change type specified")

    async with session.begin():
        current_data = await session.execute(select(residents_ratings).where(residents_ratings.c.id == rating_id))
        current_rating = current_data.mappings().first()

        if not current_rating:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")

        # Получаем изначальный рейтинг
        initial_overall_score = current_rating['overall_score']

        # Уменьшаем infraction_score
        new_infraction_score = max(0, current_rating['infraction_score'] + decrement)

        # Пересчитываем общий рейтинг с учетом изначального значения
        new_overall_score = max(1, min(5,  initial_overall_score - decrement))

        await session.execute(
            update(residents_ratings).where(residents_ratings.c.id == rating_id).values(
                infraction_score=new_infraction_score,
                overall_score=new_overall_score
            )
        )

    return {"status": "success", "message": "Infraction score decreased successfully"}

