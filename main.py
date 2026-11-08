from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
import models
import schemas

app = FastAPI(title="Склад небольшого магазина API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/")
def read_root():
    return {"message": "Сервер FastAPI успешно запущен!"}

@app.get("/api/v1/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return JSONResponse(
        content=jsonable_encoder(products),
        media_type="application/json; charset=utf-8"
    )

# Маршрут для регистрации нового пользователя
@app.post("/api/v1/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверяем, нет ли уже пользователя с таким именем
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    
    # Хешируем пароль перед сохранением
    hashed_password = pwd_context.hash(user.password)
    
    # Создаем нового пользователя
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Пользователь успешно зарегистрирован", "user_id": new_user.id, "role": new_user.role}