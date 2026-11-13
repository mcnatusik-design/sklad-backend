from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import openpyxl
from openpyxl.styles import Font, Alignment

from database import get_db
import models
import schemas

load_dotenv()

app = FastAPI(title="Склад небольшого магазина API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"message": "Сервер FastAPI успешно запущен!"}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- АУТЕНТИФИКАЦИЯ (ПР 5) ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/api/v1/login", tags=["Auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# --- CRUD ТОВАРОВ ---
@app.get("/api/v1/products", tags=["Products"])
def get_products(skip: int = 0, limit: int = 10, search: str = "", db: Session = Depends(get_db)):
    query = db.query(models.Product)
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
    products = query.offset(skip).limit(limit).all()
    return JSONResponse(content=jsonable_encoder(products), media_type="application/json; charset=utf-8")

@app.post("/api/v1/products", status_code=status.HTTP_201_CREATED, tags=["Products"])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_product = models.Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.put("/api/v1/products/{product_id}", tags=["Products"])
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/api/v1/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    db.delete(db_product)
    db.commit()
    return None

# --- РЕГИСТРАЦИЯ ---
@app.post("/api/v1/register", status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=409, detail="Пользователь с таким именем уже существует") # 409 Conflict
    hashed_password = pwd_context.hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Пользователь успешно зарегистрирован", "user_id": new_user.id, "role": new_user.role}

# --- АНАЛИТИКА (ПР 4) ---
@app.get("/api/v1/analytics/summary", tags=["Analytics"])
def get_summary(month: str = None, db: Session = Depends(get_db)):
    query = db.query(func.sum(models.Sale.total_amount))
    if month and month != "all":
        query = query.filter(func.to_char(models.Sale.date, 'YYYY-MM') == month)
    total_sales = query.scalar() or 0
    total_products = db.query(func.count(models.Product.id)).scalar() or 0
    low_stock_count = db.query(func.count(models.Product.id)).filter(models.Product.current_stock <= models.Product.min_stock).scalar() or 0
    return {"total_sales": round(total_sales, 2), "total_products": total_products, "low_stock_count": low_stock_count}

@app.get("/api/v1/analytics/sales_by_month", tags=["Analytics"])
def get_sales_by_month(month: str = None, db: Session = Depends(get_db)):
    query = db.query(
        func.to_char(models.Sale.date, 'YYYY-MM').label('month'),
        func.sum(models.Sale.total_amount).label('total')
    )
    if month and month != "all":
        query = query.filter(func.to_char(models.Sale.date, 'YYYY-MM') == month)
    sales = query.group_by('month').order_by('month').all()
    return [{"month": s.month, "total": round(s.total, 2)} for s in sales]

@app.get("/api/v1/analytics/stock_by_category", tags=["Analytics"])
def get_stock_by_category(month: str = None, db: Session = Depends(get_db)):
    if month and month != "all":
        query = db.query(
            models.Category.name,
            func.sum(models.SaleItem.quantity).label('total_stock')
        ).join(models.Product, models.Category.id == models.Product.category_id)\
         .join(models.SaleItem, models.Product.id == models.SaleItem.product_id)\
         .join(models.Sale, models.SaleItem.sale_id == models.Sale.id)\
         .filter(func.to_char(models.Sale.date, 'YYYY-MM') == month)\
         .group_by(models.Category.name)
    else:
        query = db.query(
            models.Category.name,
            func.sum(models.Product.current_stock).label('total_stock')
        ).join(models.Product).group_by(models.Category.name)
    stock = query.all()
    return [{"category": s.name, "total_stock": s.total_stock} for s in stock]

@app.get("/api/v1/analytics/low_stock", tags=["Analytics"])
def get_low_stock(db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.current_stock <= models.Product.min_stock).all()
    return JSONResponse(content=jsonable_encoder(products), media_type="application/json; charset=utf-8")

# --- ДОКУМЕНТЫ (ПР 4) ---
@app.get("/api/v1/documents/invoice/{sale_id}", tags=["Documents"])
def generate_invoice_pdf(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Продажа не найдена")
    items = db.query(models.SaleItem).filter(models.SaleItem.sale_id == sale_id).all()
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        pdfmetrics.registerFont(TTFont('Arial', '/System/Library/Fonts/Supplemental/Arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
        font_name = 'Arial'
        bold_font_name = 'Arial-Bold'
    except:
        font_name = 'Helvetica'
        bold_font_name = 'Helvetica-Bold'
    p.setFont(font_name, 18)
    p.drawString(220, 800, "Товарная накладная")
    p.setFont(font_name, 12)
    p.drawString(50, 760, f"Номер чека: {sale.id}")
    p.drawString(50, 740, f"Дата: {sale.date.strftime('%d.%m.%Y')}")
    table_data = [["Наименование", "Кол-во", "Цена", "Сумма"]]
    for item in items:
        prod = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        prod_name = prod.name if prod else "Неизвестно"
        table_data.append([prod_name, str(item.quantity), f"{item.selling_price:.2f}", f"{item.quantity * item.selling_price:.2f}"])
    table_data.append(["", "", "ИТОГО:", f"{sale.total_amount:.2f}"])
    table = Table(table_data, colWidths=[250, 60, 80, 100])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), bold_font_name)
    ])
    table.setStyle(style)
    w, h = table.wrapOn(p, 500, 500)
    table.drawOn(p, 50, 650 - h)
    p.showPage()
    p.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=invoice_{sale.id}.pdf"})

@app.get("/api/v1/documents/stock_excel", tags=["Documents"])
def generate_stock_excel(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Остатки на складе"
    headers = ["ID", "Название", "Цена", "Остаток", "Мин. остаток"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")
    for prod in products:
        ws.append([prod.id, prod.name, prod.price, prod.current_stock, prod.min_stock])
    for col in ws.columns:
        max_length = max(len(str(cell.value)) for cell in col if cell.value)
        ws.column_dimensions[col[0].column_letter].width = max_length + 2
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=stock_report.xlsx"})