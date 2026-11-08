import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Загружаем переменные из файла .env
load_dotenv()

# Берем ссылку на базу данных из настроек
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем движок (подключение)
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"client_encoding": "utf8"})

# Создаем сессию для запросов к базе
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для создания таблиц
Base = declarative_base()

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()