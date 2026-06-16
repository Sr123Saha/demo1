# database.py
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from config import DB_PATH

def get_connection():
    """Получение соединения с БД"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """Создание таблиц, если их нет"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Создаём таблицы
        cursor.executescript("""
            -- Таблица пользователей
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            
            -- Таблица товаров
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                unit TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                supplier TEXT NOT NULL,
                manufacturer TEXT NOT NULL,
                category TEXT NOT NULL,
                discount INTEGER DEFAULT 0 CHECK(discount >= 0 AND discount <= 100),
                quantity INTEGER DEFAULT 0 CHECK(quantity >= 0),
                description TEXT,
                image_path TEXT
            );
            
            -- Таблица пунктов выдачи
            CREATE TABLE IF NOT EXISTS PickupPoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT NOT NULL UNIQUE
            );
            
            -- Таблица заказов
            CREATE TABLE IF NOT EXISTS Orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number INTEGER UNIQUE NOT NULL,
                order_date TEXT NOT NULL,
                delivery_date TEXT,
                pickup_point_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                pickup_code TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Новый', 'Завершен')),
                FOREIGN KEY (pickup_point_id) REFERENCES PickupPoints(id) ON DELETE RESTRICT,
                FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE RESTRICT
            );
            
            -- Таблица состава заказа
            CREATE TABLE IF NOT EXISTS OrderItems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                FOREIGN KEY (order_id) REFERENCES Orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES Products(id) ON DELETE RESTRICT,
                UNIQUE(order_id, product_id)
            );
            
            -- Индексы для ускорения поиска
            CREATE INDEX IF NOT EXISTS idx_products_name ON Products(name);
            CREATE INDEX IF NOT EXISTS idx_products_category ON Products(category);
            CREATE INDEX IF NOT EXISTS idx_orders_user ON Orders(user_id);
            CREATE INDEX IF NOT EXISTS idx_orders_status ON Orders(status);
        """)
        
        conn.commit()
        print(" База данных инициализирована")



def get_user_by_login_password(login, password):
    """Проверка авторизации"""
    hashed = hash_password(password)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, role, full_name, login 
            FROM Users 
            WHERE login = ? AND password = ?
        """, (login, hashed))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_id(user_id):
    """Получение пользователя по ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, role, full_name, login FROM Users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_all_users():
    """Получение всех пользователей"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, role, full_name, login FROM Users ORDER BY full_name")
        return [dict(row) for row in cursor.fetchall()]


def get_all_products(filters=None):
    """Получение списка товаров с фильтрацией"""
    query = "SELECT * FROM Products WHERE 1=1"
    params = []
    
    if filters:
        # Поиск по тексту
        if filters.get('search'):
            search_term = f"%{filters['search']}%"
            query += " AND (name LIKE ? OR category LIKE ? OR manufacturer LIKE ? OR description LIKE ? OR article LIKE ?)"
            params.extend([search_term] * 5)
        
        # Фильтр по скидке
        if filters.get('discount_range'):
            if filters['discount_range'] == '0-12.99':
                query += " AND discount BETWEEN 0 AND 12.99"
            elif filters['discount_range'] == '13-16.99':
                query += " AND discount BETWEEN 13 AND 16.99"
            elif filters['discount_range'] == '17+':
                query += " AND discount >= 17"
        
        # Сортировка
        if filters.get('sort_by'):
            order = filters.get('sort_order', 'ASC')
            query += f" ORDER BY {filters['sort_by']} {order}"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_product_by_id(product_id):
    """Получение товара по ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_product_by_article(article):
    """Получение товара по артикулу"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products WHERE article = ?", (article,))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_product(product_data):
    """Добавление нового товара"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Products 
            (article, name, unit, price, supplier, manufacturer, 
             category, discount, quantity, description, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_data['article'],
            product_data['name'],
            product_data['unit'],
            product_data['price'],
            product_data['supplier'],
            product_data['manufacturer'],
            product_data['category'],
            product_data['discount'],
            product_data['quantity'],
            product_data['description'],
            product_data.get('image_path', '')
        ))
        conn.commit()
        return cursor.lastrowid

def update_product(product_id, product_data):
    """Обновление товара"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Products SET
                article = ?, name = ?, unit = ?, price = ?,
                supplier = ?, manufacturer = ?, category = ?,
                discount = ?, quantity = ?, description = ?,
                image_path = ?
            WHERE id = ?
        """, (
            product_data['article'],
            product_data['name'],
            product_data['unit'],
            product_data['price'],
            product_data['supplier'],
            product_data['manufacturer'],
            product_data['category'],
            product_data['discount'],
            product_data['quantity'],
            product_data['description'],
            product_data.get('image_path', ''),
            product_id
        ))
        conn.commit()

def delete_product(product_id):
    """Удаление товара (проверяет наличие в заказах)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Проверяем, есть ли товар в заказах
        cursor.execute("SELECT COUNT(*) as count FROM OrderItems WHERE product_id = ?", (product_id,))
        result = cursor.fetchone()
        if result['count'] > 0:
            raise Exception("Нельзя удалить товар, который присутствует в заказах")
        
        # Если нет, удаляем
        cursor.execute("DELETE FROM Products WHERE id = ?", (product_id,))
        conn.commit()

def search_products(search_text):
    """Поиск товаров по тексту"""
    with get_connection() as conn:
        cursor = conn.cursor()
        search_term = f"%{search_text}%"
        cursor.execute("""
            SELECT * FROM Products 
            WHERE name LIKE ? OR article LIKE ? OR category LIKE ?
            LIMIT 20
        """, (search_term, search_term, search_term))
        return [dict(row) for row in cursor.fetchall()]

def get_product_categories():
    """Получение всех уникальных категорий"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM Products ORDER BY category")
        return [row['category'] for row in cursor.fetchall()]

def get_product_suppliers():
    """Получение всех уникальных поставщиков"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT supplier FROM Products ORDER BY supplier")
        return [row['supplier'] for row in cursor.fetchall()]



def get_all_orders(filters=None):
    """Получение списка заказов"""
    query = """
        SELECT o.*, u.full_name as client_name, p.address as pickup_address
        FROM Orders o
        LEFT JOIN Users u ON o.user_id = u.id
        LEFT JOIN PickupPoints p ON o.pickup_point_id = p.id
        WHERE 1=1
    """
    params = []
    
    if filters and filters.get('status'):
        query += " AND o.status = ?"
        params.append(filters['status'])
    
    query += " ORDER BY o.order_date DESC"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_order_by_id(order_id):
    """Получение заказа по ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.*, u.full_name as client_name, p.address as pickup_address
            FROM Orders o
            LEFT JOIN Users u ON o.user_id = u.id
            LEFT JOIN PickupPoints p ON o.pickup_point_id = p.id
            WHERE o.id = ?
        """, (order_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_order_items(order_id):
    """Получение состава заказа"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT oi.*, p.article, p.name as product_name, p.price
            FROM OrderItems oi
            JOIN Products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        """, (order_id,))
        return [dict(row) for row in cursor.fetchall()]

def add_order(order_data, items):
    """Добавление нового заказа"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Orders 
            (order_number, order_date, delivery_date, pickup_point_id, 
             user_id, pickup_code, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            order_data['order_number'],
            order_data['order_date'],
            order_data['delivery_date'],
            order_data['pickup_point_id'],
            order_data['user_id'],
            order_data['pickup_code'],
            order_data['status']
        ))
        order_id = cursor.lastrowid
        
        for item in items:
            cursor.execute("""
                INSERT INTO OrderItems (order_id, product_id, quantity)
                VALUES (?, ?, ?)
            """, (order_id, item['product_id'], item['quantity']))
        
        conn.commit()
        return order_id

def update_order(order_id, order_data, items):
    """Обновление заказа"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Orders SET
                order_number = ?, order_date = ?, delivery_date = ?,
                pickup_point_id = ?, user_id = ?, pickup_code = ?,
                status = ?
            WHERE id = ?
        """, (
            order_data['order_number'],
            order_data['order_date'],
            order_data['delivery_date'],
            order_data['pickup_point_id'],
            order_data['user_id'],
            order_data['pickup_code'],
            order_data['status'],
            order_id
        ))
        
        cursor.execute("DELETE FROM OrderItems WHERE order_id = ?", (order_id,))
        for item in items:
            cursor.execute("""
                INSERT INTO OrderItems (order_id, product_id, quantity)
                VALUES (?, ?, ?)
            """, (order_id, item['product_id'], item['quantity']))
        
        conn.commit()

def delete_order(order_id):
    """Удаление заказа"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Orders WHERE id = ?", (order_id,))
        conn.commit()


def get_all_pickup_points():
    """Получение всех пунктов выдачи"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, address FROM PickupPoints ORDER BY address")
        return [dict(row) for row in cursor.fetchall()]

def add_pickup_point(address):
    """Добавление нового пункта выдачи"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO PickupPoints (address) VALUES (?)", (address,))
        conn.commit()
        return cursor.lastrowid
    
    # database.py (добавь timeout в get_connection)

def get_connection():
    """Получение соединения с БД"""
    conn = sqlite3.connect(DB_PATH, timeout=10)  # Добавляем timeout
    conn.row_factory = sqlite3.Row
    return conn