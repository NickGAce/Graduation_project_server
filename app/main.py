from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.auth.base_config import auth_backend, fastapi_users
from app.auth.schemas import UserRead, UserCreate, UserUpdate


from app.room.management_room_router import router as room_router
from app.room.management_block_router import router as block_router
from app.room.management_floor_router import router as floor_router
from app.room.management_router import router as management
from app.residents.residents import router as residents
from app.comments.comments import router as comments
from app.commonRooms.commonRooms import router as common_rooms
from app.commonRooms.bookings import router as bookings
from app.ratings.ratings import router as ratings


app = FastAPI(
    title="Diplom"
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


app.include_router(room_router)
app.include_router(block_router)
app.include_router(floor_router)
app.include_router(management)
app.include_router(residents)
app.include_router(comments)
app.include_router(common_rooms)
app.include_router(bookings)
app.include_router(ratings)

origins = [
    "http://localhost:3000",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)

