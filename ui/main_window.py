# ui/main_window.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import get_all_products, delete_product, get_all_orders, delete_order
from ui.product_window import ProductWindow
from ui.order_window import OrderWindow
from config import COLORS, IMAGES_DIR, RESOURCES_DIR
import os

class MainWindow(QMainWindow):
    def __init__(self, user_data=None):
        super().__init__()
        self.user = user_data
        self.is_admin = user_data and user_data['role'] == 'Администратор'
        self.is_manager = user_data and user_data['role'] == 'Менеджер'
        self.is_client = user_data and user_data['role'] == 'Авторизированный клиент'
        self.is_guest = user_data is None
        
        self.setWindowTitle("ЧитайГород")
        self.setGeometry(100, 50, 1400, 800)
        self.current_filters = {}
        
        icon_path = RESOURCES_DIR / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Верхняя панель
        top_panel = QHBoxLayout()
        
        logo_label = QLabel()
        logo_path = RESOURCES_DIR / "logo.png"
        if not logo_path.exists():
            logo_path = RESOURCES_DIR / "icon.png"
        
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(pixmap)
                top_panel.addWidget(logo_label)
        
        title_label = QLabel("ЧитайГород")
        title_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 24px; font-weight: bold; color: #2C4360;")
        top_panel.addWidget(title_label)
        top_panel.addStretch()
        
        user_text = f"{self.user['full_name']}" if self.user else "Гость"
        user_role = f"({self.user['role']})" if self.user and self.user['role'] != 'Авторизированный клиент' else ""
        self.user_label = QLabel(f"{user_text} {user_role}")
        self.user_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 14px; color: #333333; padding: 5px 15px; background-color: #ABCFCE; border-radius: 15px;")
        top_panel.addWidget(self.user_label)
        
        logout_btn = QPushButton("Выход")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-family: 'Comic Sans MS';
                font-size: 13px;
            }
            QPushButton:hover { background-color: #C82333; }
        """)
        top_panel.addWidget(logout_btn)
        main_layout.addLayout(top_panel)
        
        # Панель поиска
        if self.is_manager or self.is_admin:
            filter_panel = QWidget()
            filter_panel.setStyleSheet("background-color: #ABCFCE; border-radius: 8px;")
            filter_layout = QHBoxLayout(filter_panel)
            filter_layout.setContentsMargins(15, 10, 15, 10)
            filter_layout.setSpacing(10)
            
            search_label = QLabel("Поиск:")
            search_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px; font-weight: bold;")
            filter_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Название, категория, производитель...")
            self.search_input.textChanged.connect(self.on_filter_changed)
            self.search_input.setStyleSheet("""
                QLineEdit {
                    font-family: 'Comic Sans MS';
                    padding: 8px;
                    border: 2px solid #FFFFFF;
                    border-radius: 6px;
                    font-size: 13px;
                    background-color: #FFFFFF;
                }
                QLineEdit:focus {
                    border-color: #546F94;
                }
            """)
            filter_layout.addWidget(self.search_input)
            
            filter_layout.addSpacing(10)
            filter_label = QLabel("Скидка:")
            filter_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px; font-weight: bold;")
            filter_layout.addWidget(filter_label)
            
            self.discount_filter = QComboBox()
            self.discount_filter.addItems(["Все диапазоны", "0-12.99%", "13-16.99%", "17% и более"])
            self.discount_filter.currentTextChanged.connect(self.on_filter_changed)
            self.discount_filter.setStyleSheet("""
                QComboBox {
                    font-family: 'Comic Sans MS';
                    padding: 5px;
                    border: 2px solid #FFFFFF;
                    border-radius: 6px;
                    background-color: #FFFFFF;
                }
            """)
            filter_layout.addWidget(self.discount_filter)
            
            filter_layout.addSpacing(10)
            sort_label = QLabel("Сортировка:")
            sort_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px; font-weight: bold;")
            filter_layout.addWidget(sort_label)
            
            self.sort_combo = QComboBox()
            self.sort_combo.addItems(["По умолчанию", "Цена ↑", "Цена ↓", "Кол-во ↑", "Кол-во ↓"])
            self.sort_combo.currentTextChanged.connect(self.on_filter_changed)
            self.sort_combo.setStyleSheet("""
                QComboBox {
                    font-family: 'Comic Sans MS';
                    padding: 5px;
                    border: 2px solid #FFFFFF;
                    border-radius: 6px;
                    background-color: #FFFFFF;
                }
            """)
            filter_layout.addWidget(self.sort_combo)
            
            filter_layout.addStretch()
            main_layout.addWidget(filter_panel)
        
        # Кнопки админа
        if self.is_admin:
            btn_panel = QHBoxLayout()
            
            add_btn = QPushButton("Добавить товар")
            add_btn.clicked.connect(self.add_product)
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #546F94;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-family: 'Comic Sans MS';
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #3D5A7A; }
            """)
            btn_panel.addWidget(add_btn)
            
            delete_btn = QPushButton("Удалить товар")
            delete_btn.clicked.connect(self.delete_product)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #546F94;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-family: 'Comic Sans MS';
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #3D5A7A; }
            """)
            btn_panel.addWidget(delete_btn)
            
            orders_btn = QPushButton("Заказы")
            orders_btn.clicked.connect(self.open_orders)
            orders_btn.setStyleSheet("""
                QPushButton {
                    background-color: #546F94;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-family: 'Comic Sans MS';
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #3D5A7A; }
            """)
            btn_panel.addWidget(orders_btn)
            
            btn_panel.addStretch()
            main_layout.addLayout(btn_panel)
        
        elif self.is_manager:
            btn_panel = QHBoxLayout()
            
            orders_btn = QPushButton("Заказы")
            orders_btn.clicked.connect(self.open_orders)
            orders_btn.setStyleSheet("""
                QPushButton {
                    background-color: #546F94;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-family: 'Comic Sans MS';
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #3D5A7A; }
            """)
            btn_panel.addWidget(orders_btn)
            btn_panel.addStretch()
            main_layout.addLayout(btn_panel)
        
        # Список товаров
        self.products_container = QWidget()
        self.products_container.setStyleSheet("background-color: #FFFFFF;")
        self.products_layout = QVBoxLayout(self.products_container)
        self.products_layout.setSpacing(15)
        self.products_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.products_container)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #FFFFFF;
            }
        """)
        
        main_layout.addWidget(scroll_area)
        
        self.load_products()
    
    def load_products(self):
        for i in reversed(range(self.products_layout.count())):
            widget = self.products_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        filters = {}
        
        if hasattr(self, 'search_input') and self.search_input.text():
            filters['search'] = self.search_input.text()
        
        if hasattr(self, 'discount_filter'):
            discount_map = {
                "Все диапазоны": None,
                "0-12.99%": "0-12.99",
                "13-16.99%": "13-16.99",
                "17% и более": "17+"
            }
            discount_value = discount_map.get(self.discount_filter.currentText())
            if discount_value:
                filters['discount_range'] = discount_value
        
        if hasattr(self, 'sort_combo'):
            sort_map = {
                "По умолчанию": None,
                "Цена ↑": ("price", "ASC"),
                "Цена ↓": ("price", "DESC"),
                "Кол-во ↑": ("quantity", "ASC"),
                "Кол-во ↓": ("quantity", "DESC")
            }
            sort_value = sort_map.get(self.sort_combo.currentText())
            if sort_value:
                filters['sort_by'] = sort_value[0]
                filters['sort_order'] = sort_value[1]
        
        products = get_all_products(filters)
        
        default_path = RESOURCES_DIR / "picture.png"
        default_pixmap = None
        if default_path.exists():
            default_pixmap = QPixmap(str(default_path))
            if not default_pixmap.isNull():
                default_pixmap = default_pixmap.scaled(120, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        for product in products:
            card = QWidget()
            card.setStyleSheet("""
                QWidget {
                    background-color: #ABCFCE;
                    border: 2px solid #546F94;
                    border-radius: 10px;
                }
            """)
            
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(15, 15, 15, 15)
            card_layout.setSpacing(20)
            
            photo_label = QLabel()
            photo_label.setFixedSize(120, 160)
            photo_label.setStyleSheet("border: 1px solid #FFFFFF; border-radius: 6px; background-color: #FFFFFF;")
            photo_label.setAlignment(Qt.AlignCenter)
            
            if product.get('image_path') and os.path.exists(str(IMAGES_DIR / product['image_path'])):
                pixmap = QPixmap(str(IMAGES_DIR / product['image_path']))
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(120, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    photo_label.setPixmap(pixmap)
                elif default_pixmap:
                    photo_label.setPixmap(default_pixmap)
            elif default_pixmap:
                photo_label.setPixmap(default_pixmap)
            
            card_layout.addWidget(photo_label)
            
            info_widget = QWidget()
            info_layout = QHBoxLayout(info_widget)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(20)
            
            text_widget = QWidget()
            text_layout = QVBoxLayout(text_widget)
            text_layout.setSpacing(4)
            text_layout.setContentsMargins(0, 0, 0, 0)
            
            header_label = QLabel(f"{product['category']} | {product['name']}")
            header_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 16px; font-weight: bold; color: #2C4360;")
            text_layout.addWidget(header_label)
            
            desc_label = QLabel(f"Описание товара: {product['description'] or 'Нет описания'}")
            desc_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px; color: #333333;")
            desc_label.setWordWrap(True)
            text_layout.addWidget(desc_label)
            
            text_layout.addWidget(QLabel(f"Производитель: {product['manufacturer']}"))
            text_layout.itemAt(text_layout.count() - 1).widget().setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px; color: #333333;")
            
            text_layout.addWidget(QLabel(f"Поставщик: {product['supplier']}"))
            text_layout.itemAt(text_layout.count() - 1).widget().setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px; color: #333333;")
            
            original_price = product['price']
            discount = product['discount']
            
            if discount > 0:
                new_price = original_price * (1 - discount / 100)
                price_text = f"Цена: {original_price:.2f} ₽ → {new_price:.2f} ₽"
                price_label = QLabel(price_text)
                price_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px; font-family: 'Comic Sans MS';")
            else:
                price_text = f"Цена: {original_price:.2f} ₽"
                price_label = QLabel(price_text)
                price_label.setStyleSheet("color: #333333; font-size: 14px; font-family: 'Comic Sans MS';")
            text_layout.addWidget(price_label)
            
            text_layout.addWidget(QLabel(f"Единица измерения: {product['unit']}"))
            text_layout.itemAt(text_layout.count() - 1).widget().setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px; color: #333333;")
            
            qty_text = f"Количество на складе: {product['quantity']}"
            qty_label = QLabel(qty_text)
            if product['quantity'] == 0:
                qty_label.setStyleSheet("color: #808080; font-family: 'Comic Sans MS'; font-size: 13px;")
            else:
                qty_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px; color: #333333;")
            text_layout.addWidget(qty_label)
            
            if self.is_admin:
                btn_row = QHBoxLayout()
                btn_row.setSpacing(10)
                
                edit_btn = QPushButton("Изменить")
                edit_btn.setFixedWidth(80)
                edit_btn.clicked.connect(lambda checked, p=product: self.edit_product_by_article(p['article']))
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #546F94;
                        color: white;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 4px;
                        font-family: 'Comic Sans MS';
                        font-size: 12px;
                    }
                    QPushButton:hover { background-color: #3D5A7A; }
                """)
                btn_row.addWidget(edit_btn)
                
                delete_btn = QPushButton("Удалить")
                delete_btn.setFixedWidth(80)
                delete_btn.clicked.connect(lambda checked, p=product: self.delete_product_by_id(p['id'], p['article'], p['name']))
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #DC3545;
                        color: white;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 4px;
                        font-family: 'Comic Sans MS';
                        font-size: 12px;
                    }
                    QPushButton:hover { background-color: #C82333; }
                """)
                btn_row.addWidget(delete_btn)
                btn_row.addStretch()
                
                text_layout.addLayout(btn_row)
            
            text_layout.addStretch()
            info_layout.addWidget(text_widget)
            
            discount_widget = QWidget()
            discount_widget.setFixedWidth(120)
            
            discount_layout = QVBoxLayout(discount_widget)
            discount_layout.setAlignment(Qt.AlignCenter)
            discount_layout.setContentsMargins(10, 10, 10, 10)
            
            discount_title = QLabel("Скидка")
            discount_title.setAlignment(Qt.AlignCenter)
            discount_title.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 14px; color: #333333; font-weight: bold;")
            discount_layout.addWidget(discount_title)
            
            discount_value = QLabel(f"{discount}%")
            discount_value.setAlignment(Qt.AlignCenter)
            discount_value.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 32px; color: #333333; font-weight: bold;")
            discount_layout.addWidget(discount_value)
            
            if discount == 0:
                discount_widget.hide()
                discount_widget.setFixedWidth(0)
            elif discount > 25:
                discount_widget.setStyleSheet("""
                    QWidget {
                        background-color: #23E1EF;
                        border-radius: 10px;
                    }
                """)
            else:
                discount_widget.setStyleSheet("""
                    QWidget {
                        background-color: #FFFFFF;
                        border-radius: 10px;
                    }
                """)
            
            info_layout.addWidget(discount_widget)
            card_layout.addWidget(info_widget)
            
            if product['quantity'] == 0:
                card.setStyleSheet("""
                    QWidget {
                        background-color: #D3D3D3;
                        border: 2px solid #546F94;
                        border-radius: 10px;
                    }
                """)
            
            self.products_layout.addWidget(card)
        
        if len(products) == 0:
            empty_label = QLabel("Товаров не найдено")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 18px; color: #888888; padding: 50px;")
            self.products_layout.addWidget(empty_label)
    
    def on_filter_changed(self):
        self.load_products()
    
    def add_product(self):
        self.product_window = ProductWindow(self)
        self.product_window.show()
    
    def edit_product_by_article(self, article):
        self.product_window = ProductWindow(self, article)
        self.product_window.show()
    
    def delete_product(self):
        products = get_all_products()
        if not products:
            QMessageBox.warning(self, "Внимание", "Нет товаров для удаления")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите товар для удаления")
        dialog.setFixedSize(500, 400)
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Выберите товар:"))
        
        list_widget = QListWidget()
        for p in products:
            list_widget.addItem(f"{p['article']} - {p['name']}")
        layout.addWidget(list_widget)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("Удалить")
        ok_btn.setStyleSheet("background-color: #DC3545; color: white; border: none; padding: 8px 20px; border-radius: 4px; font-family: 'Comic Sans MS';")
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("background-color: #6C757D; color: white; border: none; padding: 8px 20px; border-radius: 4px; font-family: 'Comic Sans MS';")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            current_item = list_widget.currentItem()
            if current_item:
                text = current_item.text()
                article = text.split(" - ")[0]
                for p in products:
                    if p['article'] == article:
                        self.delete_product_by_id(p['id'], p['article'], p['name'])
                        break
    
    def delete_product_by_id(self, product_id, article, name):
        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            f'Вы уверены, что хотите удалить товар "{name}" ({article})?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                delete_product(product_id)
                self.load_products()
                QMessageBox.information(self, "Успех", "Товар успешно удалён")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
    
    def open_orders(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Управление заказами")
        dialog.setGeometry(100, 50, 1000, 700)
        dialog.setModal(False)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("Список заказов")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C4360; font-family: 'Comic Sans MS';")
        layout.addWidget(title)
        
        if self.is_admin:
            add_btn = QPushButton("Добавить заказ")
            add_btn.clicked.connect(lambda: self.add_order(dialog))
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #546F94;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-family: 'Comic Sans MS';
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #3D5A7A; }
            """)
            layout.addWidget(add_btn)
        
        orders_container = QWidget()
        orders_container.setStyleSheet("background-color: #FFFFFF;")
        orders_layout = QVBoxLayout(orders_container)
        orders_layout.setSpacing(15)
        orders_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(orders_container)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #FFFFFF;
            }
        """)
        
        layout.addWidget(scroll_area)
        
        def load_orders():
            for i in reversed(range(orders_layout.count())):
                widget = orders_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            orders = get_all_orders()
            
            for order in orders:
                card = QWidget()
                card.setStyleSheet("""
                    QWidget {
                        background-color: #ABCFCE;
                        border: 2px solid #546F94;
                        border-radius: 10px;
                    }
                """)
                
                card_layout = QHBoxLayout(card)
                card_layout.setContentsMargins(15, 15, 15, 15)
                card_layout.setSpacing(20)
                
                # ЛЕВАЯ ЧАСТЬ
                info_widget = QWidget()
                info_layout = QVBoxLayout(info_widget)
                info_layout.setSpacing(4)
                info_layout.setContentsMargins(0, 0, 0, 0)
                
                order_label = QLabel(f"Артикул заказа: {order['order_number']}")
                order_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 16px; font-weight: bold; color: #2C4360;")
                info_layout.addWidget(order_label)
                
                status_label = QLabel(f"Статус заказа: {order['status']}")
                if order['status'] == 'Новый':
                    status_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 14px; color: #FF8C00; font-weight: bold;")
                else:
                    status_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 14px; color: #28A745; font-weight: bold;")
                info_layout.addWidget(status_label)
                
                pickup_address = order.get('pickup_address') or 'Не указан'
                info_layout.addWidget(QLabel(f"Адрес пункта выдачи: {pickup_address}"))
                info_layout.itemAt(info_layout.count() - 1).widget().setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px; color: #333333;")
                
                info_layout.addWidget(QLabel(f"Дата заказа: {order['order_date']}"))
                info_layout.itemAt(info_layout.count() - 1).widget().setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px; color: #333333;")
                
                client_name = order.get('client_name') or 'Неизвестно'
                info_layout.addWidget(QLabel(f"Клиент: {client_name}"))
                info_layout.itemAt(info_layout.count() - 1).widget().setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px; color: #333333;")
                
                info_layout.addWidget(QLabel(f"Код получения: {order['pickup_code']}"))
                info_layout.itemAt(info_layout.count() - 1).widget().setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px; color: #333333;")
                
                info_layout.addStretch()
                card_layout.addWidget(info_widget)
                
                # ПРАВАЯ ЧАСТЬ
                right_widget = QWidget()
                right_widget.setFixedWidth(200)
                right_layout = QVBoxLayout(right_widget)
                right_layout.setAlignment(Qt.AlignCenter)
                right_layout.setSpacing(10)
                
                delivery_date = order.get('delivery_date') or 'Не указана'
                delivery_label = QLabel(delivery_date)
                delivery_label.setAlignment(Qt.AlignCenter)
                delivery_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 18px; color: #2C4360; font-weight: bold;")
                right_layout.addWidget(delivery_label)
                
                if self.is_admin:
                    edit_btn = QPushButton("Изменить")
                    edit_btn.setFixedWidth(150)
                    edit_btn.setFixedHeight(35)
                    edit_btn.clicked.connect(lambda checked, o=order['id']: self.edit_order(dialog, o))
                    edit_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #546F94;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            font-family: 'Comic Sans MS';
                            font-size: 13px;
                        }
                        QPushButton:hover { background-color: #3D5A7A; }
                    """)
                    right_layout.addWidget(edit_btn)
                    
                    delete_btn = QPushButton("Удалить")
                    delete_btn.setFixedWidth(150)
                    delete_btn.setFixedHeight(35)
                    delete_btn.clicked.connect(lambda checked, o=order['id']: self.delete_order(dialog, o))
                    delete_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #DC3545;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            font-family: 'Comic Sans MS';
                            font-size: 13px;
                        }
                        QPushButton:hover { background-color: #C82333; }
                    """)
                    right_layout.addWidget(delete_btn)
                
                card_layout.addWidget(right_widget)
                orders_layout.addWidget(card)
            
            if len(orders) == 0:
                empty_label = QLabel("Заказов не найдено")
                empty_label.setAlignment(Qt.AlignCenter)
                empty_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 18px; color: #888888; padding: 50px;")
                orders_layout.addWidget(empty_label)
        
        load_orders()
        dialog.load_orders = load_orders
        dialog.exec_()
    
    def add_order(self, parent_dialog):
        from ui.order_window import OrderWindow
        order_window = OrderWindow(self)
        order_window.show()
        if parent_dialog:
            parent_dialog.accept()
    
    def edit_order(self, parent_dialog, order_id):
        from ui.order_window import OrderWindow
        order_window = OrderWindow(self, order_id)
        order_window.show()
        if parent_dialog:
            parent_dialog.accept()
    
    def delete_order(self, parent_dialog, order_id):
        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            'Вы уверены, что хотите удалить этот заказ?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                delete_order(order_id)
                QMessageBox.information(self, "Успех", "Заказ удалён")
                if parent_dialog:
                    parent_dialog.load_orders()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
    
    def logout(self):
        self.hide()
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()