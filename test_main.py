from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Переменная для хранения токена
auth_token = ""

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_login_success():
    global auth_token
    response = client.post("/api/v1/login", data={"username": "admin", "password": "secret123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    auth_token = response.json()["access_token"]

def test_login_fail():
    response = client.post("/api/v1/login", data={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверное имя пользователя или пароль"

def test_get_products():
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_product_without_token():
    response = client.post("/api/v1/products", json={"name": "Тестовый товар", "category_id": 1, "price": 100.0})
    assert response.status_code == 401

def test_create_product_with_token():
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post(
        "/api/v1/products", 
        json={"name": "Тестовый товар", "category_id": 1, "price": 100.0, "current_stock": 10, "min_stock": 5},
        headers=headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Тестовый товар"

def test_update_nonexistent_product():
    response = client.put(
        "/api/v1/products/99999", 
        json={"name": "Обновленный товар", "category_id": 1, "price": 100.0, "current_stock": 10, "min_stock": 5},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Товар не найден"

def test_delete_product_without_token():
    response = client.delete("/api/v1/products/1")
    assert response.status_code == 401

def test_delete_product_with_token():
    # Получаем список, чтобы узнать ID последнего созданного товара
    response_list = client.get("/api/v1/products?limit=100")
    product_id = response_list.json()[-1]["id"]
    
    response = client.delete(
        f"/api/v1/products/{product_id}", 
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204

def test_register_invalid_data():
    response = client.post("/api/v1/register", json={})
    assert response.status_code == 422

def test_delete_product_forbidden():
    # Регистрируем кладовщика
    client.post("/api/v1/register", json={"username": "worker_test", "password": "123", "role": "worker"})
    
    # Логинимся под ним
    response_login = client.post("/api/v1/login", data={"username": "worker_test", "password": "123"})
    worker_token = response_login.json()["access_token"]
    
    # Пытаемся удалить товар (должны получить 403)
    response = client.delete(
        "/api/v1/products/1", 
        headers={"Authorization": f"Bearer {worker_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Недостаточно прав для удаления"