from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "worker" # По умолчанию создаем кладовщика

class UserLogin(BaseModel):
    username: str
    password: str

class ProductCreate(BaseModel):
    name: str
    category_id: int
    price: float
    current_stock: int = 0
    min_stock: int = 5