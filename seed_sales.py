from database import SessionLocal
from models import Sale, SaleItem, Product
import random
import datetime

def seed_sales():
    db = SessionLocal()
    if db.query(Sale).first():
        print("База данных уже содержит продажи!")
        db.close()
        return

    products = db.query(Product).all()
    if not products:
        print("Сначала добавьте товары!")
        db.close()
        return

    # Создаем 20 случайных продаж за последние 6 месяцев
    for i in range(20):
        days_ago = random.randint(1, 180)
        sale_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_ago)
        
        new_sale = Sale(date=sale_date, total_amount=0)
        db.add(new_sale)
        db.commit()
        db.refresh(new_sale)

        total = 0
        # Добавляем 1-3 товара в каждый чек
        for _ in range(random.randint(1, 3)):
            prod = random.choice(products)
            qty = random.randint(1, 5)
            price = prod.price
            total += qty * price
            
            item = SaleItem(
                sale_id=new_sale.id,
                product_id=prod.id,
                quantity=qty,
                selling_price=price
            )
            db.add(item)
        
        new_sale.total_amount = total
        db.commit()

    db.close()
    print("База данных успешно наполнена тестовыми продажами!")

if __name__ == "__main__":
    seed_sales()