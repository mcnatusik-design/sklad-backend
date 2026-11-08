# Серверная часть (Backend) - Склад небольшого магазина

Этот репозиторий содержит серверную часть интернет-приложения на Python (FastAPI) и базу данных PostgreSQL.

## Инструкция по запуску
1. Создайте виртуальное окружение: `python3 -m venv venv`
2. Активируйте его: `source venv/bin/activate`
3. Установите зависимости: `pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic python-dotenv passlib[bcrypt] python-jose[cryptography]`
4. Примените миграции: `alembic upgrade head`
5. Заполните базу тестовыми данными: `python seed.py`
6. Запустите сервер: `uvicorn main:app --reload`

## Что сделано (ПР 3)
- Создана база данных PostgreSQL.
- Настроены миграции (Alembic).
- Реализованы модели (Товары, Категории, Поставки, Продажи, Пользователи).
- Реализовано хеширование паролей (bcrypt).
- Создан API для получения товаров и регистрации пользователей.
- 
