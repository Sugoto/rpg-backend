from fastapi import APIRouter, HTTPException
from db_managers.user_manager import save_user, get_user
from pydantic import BaseModel

router = APIRouter(tags=["Users"])


class User(BaseModel):
    char_name: str
    username: str
    class_name: str


router = APIRouter(tags=["Users"])


@router.post("/users")
async def create_user(user: User):
    await save_user(user.char_name, user.username, user.class_name)
    return {"message": "User saved successfully"}


@router.get("/users/{username}")
async def read_user(username: str):
    user = await get_user(username)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")
