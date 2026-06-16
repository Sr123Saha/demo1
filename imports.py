# imports.py
import pandas as pd
import shutil
from datetime import datetime
from pathlib import Path
from PIL import Image
from database import (
    get_connection, hash_password, get_product_by_article,
    add_pickup_point, get_all_pickup_points
)
from config import IMAGES_DIR, MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT

def resize_and_save_image(source_path, target_filename):
    """Изменяет размер изображения и сохраняет в папку images"""
    try:
        if not source_path.exists():
            print(f"⚠️ Файл {source_path} не найден")
            return None
        
        with Image.open(source_path) as img:
            img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.Resampling.LANCZOS)
            new_img = Image.new('RGB', (MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), (255, 255, 255))
            x = (MAX_IMAGE_WIDTH - img.width) // 2
            y = (MAX_IMAGE_HEIGHT - img.height) // 2
            new_img.paste(img, (x, y))
            target_path = IMAGES_DIR / target_filename
            new_img.save(target_path, 'JPEG', quality=85)
            return target_filename
    except Exception as e:
        print(f"❌ Ошибка при обработке {source_path}: {e}")
        return None

def import_users_from_excel(file_path):
    """Импорт пользователей из Excel"""
    try:
        df = pd.read_excel(file_path)
        
        print(f"📋 Найдено колонок: {df.columns.tolist()}")
        print(f"📋 Найдено записей: {len(df)}")
        
        with get_connection() as conn:
            cursor = conn.cursor()
            count = 0
            
            for index, row in df.iterrows():
                try:
                    role = str(row.get('Роль сотрудника', ''))
                    full_name = str(row.get('ФИО', ''))
                    login = str(row.get('Логин', ''))
                    password = str(row.get('Пароль', ''))
                    
                    if not all([role, full_name, login, password]):
                        print(f"⚠️ Пропущена строка {index+2}: не все поля заполнены")
                        continue
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO Users (role, full_name, login, password)
                        VALUES (?, ?, ?, ?)
                    """, (
                        role,
                        full_name,
                        login,
                        hash_password(password)
                    ))
                    
                    if cursor.rowcount > 0:
                        count += 1
                        print(f"  ✅ Добавлен пользователь: {full_name}")
                    else:
                        print(f"  ⚠️ Пользователь уже существует: {full_name}")
                        
                except Exception as e:
                    print(f"⚠️ Ошибка в строке {index+2}: {e}")
            
            conn.commit()
            print(f"✅ Импортировано пользователей: {count}")
            
    except Exception as e:
        print(f"❌ Ошибка при импорте пользователей: {e}")

def import_products_from_excel(file_path):
    """Импорт товаров из Excel с обработкой изображений"""
    try:
        df = pd.read_excel(file_path)
        base_dir = Path(file_path).parent
        
        with get_connection() as conn:
            cursor = conn.cursor()
            count = 0
            
            for _, row in df.iterrows():
                try:
                    description = str(row['Описание товара']) if pd.notna(row['Описание товара']) else ''
                    image_filename = str(row['Фото']) if pd.notna(row['Фото']) else ''
                    
                    image_path = ''
                    if image_filename:
                        source_image = base_dir / image_filename
                        if source_image.exists():
                            saved_name = resize_and_save_image(source_image, image_filename)
                            if saved_name:
                                image_path = saved_name
                                print(f"  📷 {image_filename} -> обработано")
                        else:
                            print(f"  ⚠️ {image_filename} не найден")
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO Products 
                        (article, name, unit, price, supplier, manufacturer, 
                         category, discount, quantity, description, image_path)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(row['Артикул']),
                        str(row['Наименование товара']),
                        str(row['Единица измерения']),
                        float(row['Цена']),
                        str(row['Поставщик']),
                        str(row['Производитель']),
                        str(row['Категория товара']),
                        int(row['Действующая скидка']),
                        int(row['Кол-во на складе']),
                        description,
                        image_path
                    ))
                    count += 1
                except Exception as e:
                    print(f"⚠️ Ошибка при импорте {row['Артикул']}: {e}")
            
            conn.commit()
            print(f"✅ Импортировано товаров: {count}")
    except Exception as e:
        print(f"❌ Ошибка при импорте товаров: {e}")

def import_pickup_points(file_path):
    """Импорт пунктов выдачи"""
    try:
        df = pd.read_excel(file_path, header=None)
        
        print(f"📋 Найдено записей пунктов выдачи: {len(df)}")
        
        with get_connection() as conn:
            cursor = conn.cursor()
            count = 0
            
            for index, row in df.iterrows():
                try:
                    address = str(row[0]).strip()
                    if not address:
                        continue
                    
                    cursor.execute("INSERT OR IGNORE INTO PickupPoints (address) VALUES (?)", (address,))
                    if cursor.rowcount > 0:
                        count += 1
                        print(f"  ✅ Добавлен пункт выдачи: {address[:50]}...")
                        
                except Exception as e:
                    print(f"⚠️ Ошибка в строке {index+2}: {e}")
            
            conn.commit()
            print(f"✅ Импортировано пунктов выдачи: {count}")
            
    except Exception as e:
        print(f"❌ Ошибка при импорте пунктов выдачи: {e}")

def import_orders_from_excel(file_path):
    """Импорт заказов из Excel (ВСЕ заказы)"""
    try:
        df = pd.read_excel(file_path)
        
        print(f"📋 Найдено заказов: {len(df)}")
        
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Получаем пользователей по ФИО
            cursor.execute("SELECT id, full_name FROM Users")
            users = {row['full_name']: row['id'] for row in cursor.fetchall()}
            print(f"📋 Найдено пользователей в БД: {len(users)}")
            
            # Получаем все пункты выдачи
            pickup_points = get_all_pickup_points()
            print(f"📋 Найдено пунктов выдачи в БД: {len(pickup_points)}")
            
            # Создаем словари для быстрого поиска
            pickup_dict = {}
            for p in pickup_points:
                pickup_dict[str(p['id'])] = p['id']
            
            address_to_id = {p['address']: p['id'] for p in pickup_points}
            
            count = 0
            
            for index, row in df.iterrows():
                try:
                    order_num = int(row['Номер заказа'])
                    print(f"\n  📝 Заказ #{order_num} (строка {index+2})")
                    
                    # Парсим артикулы
                    items_data = []
                    parts = str(row['Артикул заказа']).split(',')
                    
                    for i in range(0, len(parts), 2):
                        if i + 1 < len(parts):
                            article = parts[i].strip()
                            quantity = int(parts[i+1].strip())
                            product = get_product_by_article(article)
                            if product:
                                items_data.append({
                                    'product_id': product['id'],
                                    'quantity': quantity
                                })
                            else:
                                print(f"    ❌ Товар {article} НЕ НАЙДЕН!")
                    
                    if not items_data:
                        print(f"    ❌ Нет товаров для заказа! Пропускаем...")
                        continue
                    
                    # Находим пользователя
                    client_name = str(row['ФИО авторизированного клиента'])
                    user_id = users.get(client_name)
                    if not user_id:
                        print(f"    ❌ Пользователь {client_name} не найден!")
                        continue
                    print(f"    ✅ Клиент: {client_name} (ID: {user_id})")
                    
                    # Находим пункт выдачи
                    pickup_value = row['Адрес пункта выдачи']
                    pickup_point_id = None
                    
                    # Если это число (ID)
                    if isinstance(pickup_value, int) or (isinstance(pickup_value, str) and pickup_value.strip().isdigit()):
                        pickup_id = str(int(pickup_value))
                        if pickup_id in pickup_dict:
                            pickup_point_id = pickup_dict[pickup_id]
                            print(f"    ✅ Пункт выдачи ID: {pickup_id}")
                        else:
                            print(f"    ❌ ID {pickup_id} не найден в базе!")
                            continue
                    
                    # Если это адрес
                    elif isinstance(pickup_value, str):
                        # Проверяем, есть ли адрес в базе
                        if pickup_value in address_to_id:
                            pickup_point_id = address_to_id[pickup_value]
                            print(f"    ✅ Пункт выдачи: {pickup_value[:40]}...")
                        else:
                            # Пробуем как ID
                            pickup_id = pickup_value.strip()
                            if pickup_id in pickup_dict:
                                pickup_point_id = pickup_dict[pickup_id]
                                print(f"    ✅ Пункт выдачи ID: {pickup_id}")
                            else:
                                # Создаем новый пункт выдачи
                                cursor.execute("INSERT OR IGNORE INTO PickupPoints (address) VALUES (?)", (pickup_value,))
                                conn.commit()
                                
                                cursor.execute("SELECT id FROM PickupPoints WHERE address = ?", (pickup_value,))
                                result = cursor.fetchone()
                                if result:
                                    pickup_point_id = result['id']
                                    address_to_id[pickup_value] = pickup_point_id
                                    pickup_dict[str(pickup_point_id)] = pickup_point_id
                                    print(f"    ✅ Создан новый пункт выдачи: {pickup_value[:40]}...")
                                else:
                                    print(f"    ❌ Не удалось создать пункт выдачи: {pickup_value}")
                                    continue
                    
                    if not pickup_point_id:
                        print(f"    ❌ Не удалось определить пункт выдачи!")
                        continue
                    
                    # Обработка дат
                    order_date = row['Дата заказа']
                    if isinstance(order_date, datetime):
                        order_date_str = order_date.strftime('%Y-%m-%d')
                    else:
                        order_date_str = str(order_date)[:10]
                    
                    delivery_date = row['Дата доставки']
                    if isinstance(delivery_date, datetime):
                        delivery_date_str = delivery_date.strftime('%Y-%m-%d')
                    else:
                        delivery_date_str = str(delivery_date)[:10] if pd.notna(delivery_date) else None
                    
                    # Проверяем, есть ли уже такой заказ
                    cursor.execute("SELECT id FROM Orders WHERE order_number = ?", (order_num,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        print(f"    ⚠️ Заказ #{order_num} уже существует, обновляем...")
                        cursor.execute("DELETE FROM OrderItems WHERE order_id = ?", (existing['id'],))
                        cursor.execute("DELETE FROM Orders WHERE id = ?", (existing['id'],))
                    
                    # Создаём заказ
                    cursor.execute("""
                        INSERT INTO Orders 
                        (order_number, order_date, delivery_date, pickup_point_id, 
                         user_id, pickup_code, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        order_num,
                        order_date_str,
                        delivery_date_str,
                        pickup_point_id,
                        user_id,
                        str(row['Код для получения']),
                        str(row['Статус заказа']).strip().replace('.', '').replace(';', '')
                    ))
                    
                    order_id = cursor.lastrowid
                    for item in items_data:
                        cursor.execute("""
                            INSERT INTO OrderItems (order_id, product_id, quantity)
                            VALUES (?, ?, ?)
                        """, (order_id, item['product_id'], item['quantity']))
                    
                    count += 1
                    print(f"    ✅ Заказ #{order_num} добавлен!")
                    
                except Exception as e:
                    print(f"    ❌ Ошибка: {e}")
                    continue
            
            conn.commit()
            
            print("\n" + "=" * 50)
            print(f"✅ Импортировано заказов: {count} из {len(df)}")
            print("=" * 50)
            
    except Exception as e:
        print(f"❌ Ошибка при импорте заказов: {e}")

def import_all_data():
    """Импорт всех данных"""
    print("\n🚀 НАЧИНАЕМ ИМПОРТ ДАННЫХ\n")
    print("=" * 50)
    
    import_users_from_excel('user_import.xlsx')
    import_products_from_excel('Tovar.xlsx')
    import_pickup_points('Пункты выдачи_import.xlsx')
    import_orders_from_excel('Заказ_import.xlsx')
    
    print("\n" + "=" * 50)
    print("🎉 ИМПОРТ ЗАВЕРШЁН!")