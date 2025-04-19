from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update, insert
from app.database import get_async_session
from app.commonRooms.models import public_rooms, room_types
from app.room.models import blocks, floors
from app.commonRooms.schemas import PublicRoomCreate, PublicRoomUpdate

router = APIRouter(
    prefix="/management/public-rooms",
    tags=["Management Public Rooms"]
)

@router.get("/room_types/")
async def get_all_room_types(session: AsyncSession = Depends(get_async_session)):
    stmt = select(room_types)  # Создаем SQL запрос для выбора всех записей
    result = await session.execute(stmt)  # Выполняем запрос
    room_types_list = result.mappings().all()  # Получаем все результаты
    return room_types_list  # Возвращаем список типов комнат


# Получение всех общедоступных комнат
@router.get("/")
async def get_all_public_rooms(session: AsyncSession = Depends(get_async_session)):
    stmt = select(
        public_rooms.c.id,
        public_rooms.c.room_name,
        room_types.c.type_name.label('type_name'),
        blocks.c.block_name.label('block_name'),
        floors.c.floor_number.label('floor_number'),
        public_rooms.c.capacity,
        public_rooms.c.description
    ).select_from(
        public_rooms
        .join(room_types)
        .outerjoin(blocks, blocks.c.id == public_rooms.c.block_id)
        .outerjoin(floors, floors.c.id == public_rooms.c.floor_id)  # Изменено для непосредственной связи с floors
    ).order_by(public_rooms.c.room_name)
    result = await session.execute(stmt)
    rooms_data = result.mappings().all()
    return {"status": "success", "data": [dict(room) for room in rooms_data]}


# Получение общедоступной комнаты по ID
@router.get("/{room_id}")
async def get_public_room_by_id(room_id: int, session: AsyncSession = Depends(get_async_session)):
    stmt = select(
        public_rooms,
        room_types.c.type_name,
        blocks.c.block_name,
        floors.c.floor_number
    ).select_from(
        public_rooms
        .join(room_types)
        .outerjoin(blocks, blocks.c.id == public_rooms.c.block_id)
        .outerjoin(floors, floors.c.id == public_rooms.c.floor_id)
    ).where(public_rooms.c.id == room_id)
    result = await session.execute(stmt)
    room_data = result.mappings().first()
    if not room_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Public room not found")
    return {"status": "success", "data": dict(room_data)}


@router.post("/")
async def create_public_room(room_data: PublicRoomCreate, session: AsyncSession = Depends(get_async_session)):
    # Inserting new room and returning its data
    stmt = insert(public_rooms).values(**room_data.dict()).returning(public_rooms)
    result = await session.execute(stmt)
    new_room = result.mappings().first()

    # Fetch the room type name using type_id
    type_stmt = select(room_types.c.type_name).where(room_types.c.id == new_room['type_id'])
    type_result = await session.execute(type_stmt)
    type_name = type_result.scalar_one()

    # Fetch the floor number using floor_id
    floor_stmt = select(floors.c.floor_number).where(floors.c.id == new_room['floor_id'])
    floor_result = await session.execute(floor_stmt)
    floor_number = floor_result.scalar_one()

    # Construct response data with type name and floor number
    new_room_data = dict(new_room)
    new_room_data['type_name'] = type_name
    new_room_data['floor_number'] = floor_number

    await session.commit()
    return {"status": "success", "message": "Public room created successfully", "data": new_room_data}

# Обновление данных общедоступной комнаты
@router.patch("/{room_id}")
async def update_public_room(room_id: int, room_data: PublicRoomUpdate,
                             session: AsyncSession = Depends(get_async_session)):
    # Обновление информации о комнате
    update_stmt = update(public_rooms).where(public_rooms.c.id == room_id).values(
        **room_data.dict(exclude_unset=True)).returning(*public_rooms.c)
    result = await session.execute(update_stmt)
    await session.commit()
    updated_room = result.fetchone()

    if not updated_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комната не найдена")

    # Получаем полную информацию о комнате, включая тип, этаж и блок
    try:
        stmt = select(
            public_rooms.c.id,
            public_rooms.c.room_name,
            room_types.c.type_name,
            floors.c.floor_number,
            blocks.c.block_name,
            public_rooms.c.capacity,
            public_rooms.c.description
        ).select_from(
            public_rooms
            .join(room_types, public_rooms.c.type_id == room_types.c.id)
            .join(floors, public_rooms.c.floor_id == floors.c.id)
            .outerjoin(blocks, public_rooms.c.block_id == blocks.c.id)
        ).where(public_rooms.c.id == room_id)

        full_room_info = await session.execute(stmt)
        full_room_details = full_room_info.fetchone()
        if not full_room_details:
            raise NoResultFound("Детали комнаты не найдены после обновления")

        return {"status": "success", "message": "Общедоступная комната успешно обновлена",
                "data": full_room_details._asdict()}
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Удаление общедоступной комнаты
@router.delete("/{room_id}")
async def delete_public_room(room_id: int, session: AsyncSession = Depends(get_async_session)):
    delete_stmt = delete(public_rooms).where(public_rooms.c.id == room_id)
    result = await session.execute(delete_stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Public room not found")
    await session.commit()
    return {"status": "success", "message": "Public room deleted successfully"}
