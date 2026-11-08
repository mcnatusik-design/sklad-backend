from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "worker" # По умолчанию создаем кладовщика

class UserLogin(BaseModel):
    username: str
    password: str