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
        
        self.setWindowTitle("Книжный магазин 'ЧитайГород'")
        self.setGeometry(100, 50, 1400, 800)
        self.current_filters = {}
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Верхняя панель
        top_panel = QHBoxLayout()
        
        title_label = QLabel("📚 Каталог товаров")
        title_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 24px; font-weight: bold; color: #2C4360;")
        top_panel.addWidget(title_label)
        top_panel.addStretch()
        
        user_text = f"👤 {self.user['full_name']}" if self.user else "👤 Гость"
        user_role = f"({self.user['role']})" if self.user and self.user['role'] != 'Авторизированный клиент' else ""
        self.user_label = QLabel(f"{user_text} {user_role}")
        self.user_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 14px; color: #333333; padding: 5px 15px; background-color: #F0F0F0; border-radius: 15px;")
        top_panel.addWidget(self.user_label)
        
        logout_btn = QPushButton("🚪 Выход")
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
        
        # Панель поиска и фильтров (для менеджера и админа)
        if self.is_manager or self.is_admin:
            filter_panel = QHBoxLayout()
            
            search_label = QLabel("🔍 Поиск:")
            search_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px;")
            filter_panel.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Название, категория, производитель...")
            self.search_input.textChanged.connect(self.on_filter_changed)
            self.search_input.setStyleSheet("padding: 8px; border: 2px solid #ABCFCE; border-radius: 6px; font-family: 'Comic Sans MS';")
            filter_panel.addWidget(self.search_input)
            
            filter_panel.addSpacing(10)
            filter_label = QLabel("Скидка:")
            filter_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px;")
            filter_panel.addWidget(filter_label)
            
            self.discount_filter = QComboBox()
            self.discount_filter.addItems(["Все диапазоны", "0-12.99%", "13-16.99%", "17% и более"])
            self.discount_filter.currentTextChanged.connect(self.on_filter_changed)
            self.discount_filter.setStyleSheet("padding: 5px; font-family: 'Comic Sans MS';")
            filter_panel.addWidget(self.discount_filter)
            
            filter_panel.addSpacing(10)
            sort_label = QLabel("Сортировка:")
            sort_label.setStyleSheet("font-family: 'Comic Sans MS'; font-size: 13px;")
            filter_panel.addWidget(sort_label)
            
            self.sort_combo = QComboBox()
            self.sort_combo.addItems(["По умолчанию", "Цена ↑", "Цена ↓", "Кол-во ↑", "Кол-во ↓"])
            self.sort_combo.currentTextChanged.connect(self.on_filter_changed)
            self.sort_combo.setStyleSheet("padding: 5px; font-family: 'Comic Sans MS';")
            filter_panel.addWidget(self.sort_combo)
            
            filter_panel.addStretch()
            main_layout.addLayout(filter_panel)
        
        # Кнопки управления (для админа)
        if self.is_admin:
            btn_panel = QHBoxLayout()
            
            add_btn = QPushButton("➕ Добавить товар")
            add_btn.clicked.connect(self.add_product)
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28A745;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-family: 'Comic Sans MS';
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #218838; }
            """)
            btn_panel.addWidget(add_btn)
            
            delete_btn = QPushButton("🗑 Удалить товар")
            delete_btn.clicked.connect(self.delete_product)
            delete_btn.setStyleSheet("""
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
            btn_panel.addWidget(delete_btn)
            
            orders_btn = QPushButton("📦 Заказы")
            orders_btn.clicked.connect(self.open_orders)
            orders_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFC107;
                    color: #333333;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-family: 'Comic Sans MS';
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #E0A800; }
            """)
            btn_panel.addWidget(orders_btn)
            
            btn_panel.addStretch()
            main_layout.addLayout(btn_panel)
        
        elif self.is_manager:
            btn_panel = QHBoxLayout()
            
            orders_btn = QPushButton("📦 Заказы")
            orders_btn.clicked.connect(self.open_orders)
            orders_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFC107;
                    color: #333333;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-family: 'Comic Sans MS';
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #E0A800; }
            """)
            btn_panel.addWidget(orders_btn)
            btn_panel.addStretch()
            main_layout.addLayout(btn_panel)
        
        # Таблица товаров
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Артикул", "Наименование", "Категория", 
            "Производитель", "Цена", "Кол-во", "Скидка", "Фото"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['main_background']};
                alternate-background-color: {COLORS['secondary_background']};
                font-family: 'Comic Sans MS';
                gridline-color: #DDDDDD;
            }}
            QHeaderView::section {{
                background-color: {COLORS['secondary_background']};
                padding: 8px;
                font-weight: bold;
            }}
        """)
        
        if self.is_admin:
            self.table.doubleClicked.connect(self.edit_product)
        
        main_layout.addWidget(self.table)
        
        self.load_products()
    
    def load_products(self):
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
        
        self.table.setRowCount(len(products))
        default_pixmap = None
        default_path = RESOURCES_DIR / "picture.png"
        if default_path.exists():
            default_pixmap = QPixmap(str(default_path))
            if not default_pixmap.isNull():
                default_pixmap = default_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        for i, product in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(product['article']))
            self.table.setItem(i, 1, QTableWidgetItem(product['name']))
            self.table.setItem(i, 2, QTableWidgetItem(product['category']))
            self.table.setItem(i, 3, QTableWidgetItem(product['manufacturer']))
            
            price_widget = QWidget()
            price_layout = QHBoxLayout(price_widget)
            price_layout.setContentsMargins(5, 2, 5, 2)
            
            original_price = product['price']
            discount = product['discount']
            
            if discount > 0:
                old_price = QLabel(f"{original_price:.2f} ₽")
                old_price.setStyleSheet("color: red; text-decoration: line-through; font-size: 12px;")
                price_layout.addWidget(old_price)
                
                new_price = original_price * (1 - discount / 100)
                new_price_label = QLabel(f"{new_price:.2f} ₽")
                new_price_label.setStyleSheet("color: black; font-weight: bold; font-size: 14px;")
                price_layout.addWidget(new_price_label)
            else:
                price_label = QLabel(f"{original_price:.2f} ₽")
                price_label.setStyleSheet("color: black; font-size: 14px;")
                price_layout.addWidget(price_label)
            
            price_layout.addStretch()
            self.table.setCellWidget(i, 4, price_widget)
            
            qty_item = QTableWidgetItem(str(product['quantity']))
            if product['quantity'] == 0:
                qty_item.setBackground(QColor(COLORS['disabled']))
                qty_item.setForeground(QColor("white"))
            self.table.setItem(i, 5, qty_item)
            
            discount_item = QTableWidgetItem(f"{discount}%")
            if discount > 25:
                discount_item.setBackground(QColor(COLORS['discount_highlight']))
            self.table.setItem(i, 6, discount_item)
            
            image_path = product.get('image_path')
            photo_widget = QLabel()
            photo_widget.setAlignment(Qt.AlignCenter)
            photo_widget.setMinimumSize(80, 80)
            photo_widget.setMaximumSize(100, 80)
            photo_widget.setStyleSheet("border: 1px solid #DDDDDD; border-radius: 4px;")
            
            if image_path and os.path.exists(str(IMAGES_DIR / image_path)):
                pixmap = QPixmap(str(IMAGES_DIR / image_path))
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    photo_widget.setPixmap(pixmap)
                elif default_pixmap:
                    photo_widget.setPixmap(default_pixmap)
            elif default_pixmap:
                photo_widget.setPixmap(default_pixmap)
            
            self.table.setCellWidget(i, 7, photo_widget)
            
            if product['quantity'] == 0:
                for col in range(self.table.columnCount()):
                    item = self.table.item(i, col)
                    if item:
                        item.setBackground(QColor(COLORS['disabled']))
                        item.setForeground(QColor("white"))
    
    def on_filter_changed(self):
        self.load_products()
    
    def add_product(self):
        self.product_window = ProductWindow(self)
        self.product_window.show()
    
    def edit_product(self, index):
        row = index.row()
        article = self.table.item(row, 0).text()
        self.product_window = ProductWindow(self, article)
        self.product_window.show()
    
    def delete_product(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите товар для удаления")
            return
        
        article = self.table.item(current_row, 0).text()
        name = self.table.item(current_row, 1).text()
        
        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            f'Вы уверены, что хотите удалить товар "{name}" ({article})?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                products = get_all_products()
                for p in products:
                    if p['article'] == article:
                        delete_product(p['id'])
                        break
                self.load_products()
                QMessageBox.information(self, "Успех", "Товар успешно удалён")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
    
    def open_orders(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Управление заказами")
        dialog.setGeometry(100, 50, 1200, 700)
        dialog.setModal(False)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("📦 Список заказов")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C4360;")
        layout.addWidget(title)
        
        if self.is_admin:
            add_btn = QPushButton("➕ Добавить заказ")
            add_btn.clicked.connect(lambda: self.add_order(dialog))
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28A745;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-family: 'Comic Sans MS';
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #218838; }
            """)
            layout.addWidget(add_btn)
        
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "№", "Клиент", "Дата заказа", "Дата доставки",
            "Пункт выдачи", "Статус", "Код", "Действия"
        ])
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['main_background']};
                alternate-background-color: {COLORS['secondary_background']};
                font-family: 'Comic Sans MS';
                gridline-color: #DDDDDD;
            }}
            QHeaderView::section {{
                background-color: {COLORS['secondary_background']};
                padding: 8px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(table)
        
        def load_orders():
            orders = get_all_orders()
            table.setRowCount(len(orders))
            for i, order in enumerate(orders):
                table.setItem(i, 0, QTableWidgetItem(str(order['order_number'])))
                table.setItem(i, 1, QTableWidgetItem(order['client_name'] or 'Неизвестно'))
                table.setItem(i, 2, QTableWidgetItem(order['order_date']))
                table.setItem(i, 3, QTableWidgetItem(order['delivery_date'] or 'Не указана'))
                table.setItem(i, 4, QTableWidgetItem(order['pickup_address'] or 'Не указан'))
                
                status_item = QTableWidgetItem(order['status'])
                if order['status'] == 'Новый':
                    status_item.setBackground(QColor("#FFC107"))
                else:
                    status_item.setBackground(QColor("#28A745"))
                    status_item.setForeground(QColor("white"))
                table.setItem(i, 5, status_item)
                
                table.setItem(i, 6, QTableWidgetItem(order['pickup_code']))
                
                if self.is_admin:
                    widget = QWidget()
                    btn_layout = QHBoxLayout(widget)
                    btn_layout.setContentsMargins(2, 2, 2, 2)
                    btn_layout.setSpacing(5)
                    
                    edit_btn = QPushButton("✏️")
                    edit_btn.setFixedSize(30, 30)
                    edit_btn.clicked.connect(lambda checked, o=order['id']: self.edit_order(dialog, o))
                    btn_layout.addWidget(edit_btn)
                    
                    delete_btn = QPushButton("🗑")
                    delete_btn.setFixedSize(30, 30)
                    delete_btn.setStyleSheet("background-color: #DC3545; color: white;")
                    delete_btn.clicked.connect(lambda checked, o=order['id']: self.delete_order(dialog, o))
                    btn_layout.addWidget(delete_btn)
                    
                    table.setCellWidget(i, 7, widget)
        
        load_orders()
        dialog.load_orders = load_orders
        dialog.exec_()
    
    def add_order(self, parent_dialog):
        order_window = OrderWindow(self)
        order_window.show()
        if parent_dialog:
            parent_dialog.accept()
    
    def edit_order(self, parent_dialog, order_id):
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
        """Выход из системы - возврат в окно входа"""
        self.hide()
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()