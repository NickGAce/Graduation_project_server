from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, insert
from app.database import get_async_session
from app.comments.models import comments
from app.comments.schemas import CommentCreate, CommentUpdate
from app.auth.models import user
from app.auth.base_config import current_user

router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


@router.get("/room/{room_id}")
async def get_comments_for_room(room_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        select(comments).where(comments.c.room_id == room_id).order_by(comments.c.id)
    )
    comments_data = result.mappings().all()
    return {"status": "success", "data": comments_data}

# Получение всех комментариев
@router.get("/")
async def get_all_comments(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(comments).order_by(comments.c.id))
    comments_data = result.mappings().all()
    return {"status": "success", "data": comments_data}

# Получение комментария по ID
@router.get("/{comment_id}")
async def get_comment_by_id(comment_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(comments).where(comments.c.id == comment_id))
    comment_data = result.mappings().first()
    if not comment_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return {"status": "success", "data": comment_data}


@router.post("/")
async def create_comment(comment_data: CommentCreate, session: AsyncSession = Depends(get_async_session), user: user = Depends(current_user)):
    comment_data.user_id = user.id  # Автоматическая установка user_id текущего пользователя
    stmt = insert(comments).values(**comment_data.dict()).returning(*comments.c)
    result = await session.execute(stmt)
    await session.commit()
    created_comment = result.fetchone()  # Получаем данные созданного комментария
    if created_comment:
        # Преобразуем результат в словарь, если результат не None
        return {"status": "success", "message": "Comment created successfully", "data": created_comment._asdict()}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create comment")


@router.patch("/{comment_id}")
async def update_comment(comment_id: int, comment_data: CommentUpdate, session: AsyncSession = Depends(get_async_session), user: user = Depends(current_user)):
    # Получаем комментарий из базы данных
    result = await session.execute(select(comments).where(comments.c.id == comment_id))
    comment_datas = result.mappings().first()

    if not comment_datas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Проверяем, что текущий пользователь является автором комментария
    if comment_datas.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update this comment")

    update_stmt = update(comments).where(comments.c.id == comment_id).values(**comment_data.dict(exclude_unset=True)).returning(comments)
    result = await session.execute(update_stmt)
    await session.commit()
    updated_comments = result.mappings().first()
    if not updated_comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")
    return {"status": "success", "message": "Resident updated successfully", "data": updated_comments}


# Удаление комментария
@router.delete("/{comment_id}")
async def delete_comment(comment_id: int, session: AsyncSession = Depends(get_async_session), user: user = Depends(current_user)):
    # Получаем комментарий из базы данных
    results = await session.execute(select(comments).where(comments.c.id == comment_id))
    comment_datas = results.mappings().first()

    if not comment_datas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Проверяем, что текущий пользователь является автором комментария
    if comment_datas.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update this comment")

    delete_stmt = delete(comments).where(comments.c.id == comment_id)
    result = await session.execute(delete_stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    await session.commit()
    return {"status": "success", "message": "Comment deleted successfully"}
