from database import SessionLocal
from models import Category, Supplier, Product

def seed_db():
    db = SessionLocal()
    
    # Проверяем, есть ли уже данные, чтобы не дублировать при повторном запуске
    if db.query(Product).first():
        print("База данных уже заполнена!")
        db.close()
        return

    # 1. Создаем категории
    cat_milk = Category(name="Молочные продукты")
    cat_bread = Category(name="Хлебобулочные")
    cat_grocery = Category(name="Бакалея")
    cat_meat = Category(name="Мясо и птица")
    cat_drinks = Category(name="Напитки")
    cat_fruit = Category(name="Фрукты и овощи")
    
    db.add_all([cat_milk, cat_bread, cat_grocery, cat_meat, cat_drinks, cat_fruit])
    db.commit()

    # 2. Создаем поставщиков
    sup1 = Supplier(name='ООО "Молочный мир"', phone="+7(999)111-22-33")
    sup2 = Supplier(name='АО "Хлебозавод №1"', phone="+7(999)444-55-66")
    sup3 = Supplier(name='ООО "ОптБаза"', phone="+7(999)777-88-99")
    
    db.add_all([sup1, sup2, sup3])
    db.commit()

    # 3. Создаем товары (30 штук)
    products = [
        Product(name="Молоко 3,2%", category_id=cat_milk.id, price=85.0, current_stock=12, min_stock=5),
        Product(name="Кефир 1%", category_id=cat_milk.id, price=90.0, current_stock=8, min_stock=5),
        Product(name="Сметана 20%", category_id=cat_milk.id, price=150.0, current_stock=4, min_stock=6),
        Product(name="Творог 5%", category_id=cat_milk.id, price=120.0, current_stock=15, min_stock=10),
        Product(name="Сыр Российский", category_id=cat_milk.id, price=320.0, current_stock=3, min_stock=4),
        Product(name="Хлеб Бородинский", category_id=cat_bread.id, price=45.0, current_stock=8, min_stock=10),
        Product(name="Батон нарезной", category_id=cat_bread.id, price=40.0, current_stock=20, min_stock=10),
        Product(name="Булочка с маком", category_id=cat_bread.id, price=35.0, current_stock=12, min_stock=8),
        Product(name="Мука пшеничная", category_id=cat_grocery.id, price=80.0, current_stock=25, min_stock=10),
        Product(name="Сахар-песок 1кг", category_id=cat_grocery.id, price=75.0, current_stock=30, min_stock=15),
        Product(name="Соль поваренная", category_id=cat_grocery.id, price=25.0, current_stock=40, min_stock=20),
        Product(name="Рис круглозерный", category_id=cat_grocery.id, price=110.0, current_stock=15, min_stock=8),
        Product(name="Гречка ядрица", category_id=cat_grocery.id, price=105.0, current_stock=18, min_stock=10),
        Product(name="Макароны спагетти", category_id=cat_grocery.id, price=90.0, current_stock=22, min_stock=10),
        Product(name="Масло подсолнечное", category_id=cat_grocery.id, price=130.0, current_stock=14, min_stock=5),
        Product(name="Куриное филе", category_id=cat_meat.id, price=290.0, current_stock=5, min_stock=6),
        Product(name="Яйца куриные С1", category_id=cat_meat.id, price=110.0, current_stock=20, min_stock=15),
        Product(name="Сосиски молочные", category_id=cat_meat.id, price=250.0, current_stock=7, min_stock=5),
        Product(name="Вода питьевая 1,5л", category_id=cat_drinks.id, price=50.0, current_stock=50, min_stock=20),
        Product(name="Сок яблочный 1л", category_id=cat_drinks.id, price=95.0, current_stock=18, min_stock=10),
        Product(name="Чай черный", category_id=cat_drinks.id, price=150.0, current_stock=8, min_stock=5),
        Product(name="Кофе растворимый", category_id=cat_drinks.id, price=350.0, current_stock=6, min_stock=4),
        Product(name="Яблоки Гала", category_id=cat_fruit.id, price=120.0, current_stock=30, min_stock=15),
        Product(name="Бананы", category_id=cat_fruit.id, price=95.0, current_stock=25, min_stock=20),
        Product(name="Апельсины", category_id=cat_fruit.id, price=140.0, current_stock=10, min_stock=15),
        Product(name="Картофель", category_id=cat_fruit.id, price=45.0, current_stock=60, min_stock=30),
        Product(name="Морковь", category_id=cat_fruit.id, price=40.0, current_stock=35, min_stock=20),
        Product(name="Лук репчатый", category_id=cat_fruit.id, price=35.0, current_stock=40, min_stock=20),
        Product(name="Шоколад молочный", category_id=cat_grocery.id, price=130.0, current_stock=2, min_stock=10),
        Product(name="Печенье овсяное", category_id=cat_grocery.id, price=85.0, current_stock=12, min_stock=5)
    ]

    db.add_all(products)
    db.commit()
    db.close()
    print("База данных успешно наполнена 30 товарами!")

if __name__ == "__main__":
    seed_db()