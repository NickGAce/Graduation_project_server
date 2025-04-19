from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.commonRooms.models import room_bookings
from app.commonRooms.schemas import BookingCreate, BookingUpdate
from sqlalchemy.future import select
from sqlalchemy import update, insert, delete


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


@router.get("/room/{room_id}")
async def get_bookings_by_room(room_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        stmt = select(room_bookings).where(room_bookings.c.room_id == room_id)
        result = await session.execute(stmt)
        bookings_list = result.fetchall()
        bookings = [booking._asdict() for booking in bookings_list]
        return {"status": "success", "data": bookings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_all_bookings(session: AsyncSession = Depends(get_async_session)):
    try:
        stmt = select(room_bookings)
        result = await session.execute(stmt)
        bookings_list = result.fetchall()
        bookings = [booking._asdict() for booking in bookings_list]
        return {"status": "success", "data": bookings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=201)
async def create_booking(booking_data: BookingCreate, session: AsyncSession = Depends(get_async_session)):
    # Преобразование времени к формату без временной зоны
    booking_data.start_time = booking_data.start_time.replace(tzinfo=None)
    booking_data.end_time = booking_data.end_time.replace(tzinfo=None)

    stmt = insert(room_bookings).values(**booking_data.dict())
    result = await session.execute(stmt)
    await session.commit()
    return {"status": "success", "message": "Booking created successfully"}


@router.patch("/{booking_id}")
async def update_booking(booking_id: int, booking_data: BookingUpdate,
                         session: AsyncSession = Depends(get_async_session)):
    # Если дата обновления предоставлена, убираем информацию о временной зоне
    if booking_data.start_time:
        booking_data.start_time = booking_data.start_time.replace(tzinfo=None)
    if booking_data.end_time:
        booking_data.end_time = booking_data.end_time.replace(tzinfo=None)

    update_stmt = update(room_bookings).where(room_bookings.c.id == booking_id).values(
        **booking_data.dict(exclude_unset=True))
    result = await session.execute(update_stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    await session.commit()
    return {"status": "success", "message": "Booking updated successfully"}


@router.get("/{booking_id}")
async def get_booking(booking_id: int, session: AsyncSession = Depends(get_async_session)):
    stmt = select(room_bookings).where(room_bookings.c.id == booking_id)
    result = await session.execute(stmt)
    booking_info = result.fetchone()  # Получаем одну запись
    if not booking_info:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Преобразуем RowProxy в словарь, если запись существует
    booking_info_dict = booking_info._asdict() if booking_info else None

    return {"status": "success", "data": booking_info_dict}


@router.delete("/{booking_id}")
async def delete_booking(booking_id: int, session: AsyncSession = Depends(get_async_session)):
    delete_stmt = delete(room_bookings).where(room_bookings.c.id == booking_id)
    result = await session.execute(delete_stmt)
    await session.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"status": "success", "message": "Booking deleted successfully"}