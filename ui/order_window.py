# ui/order_window.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import (
    get_all_orders, get_order_by_id, get_order_items,
    get_all_products, get_all_users, get_all_pickup_points,
    add_order, update_order, delete_order,
    get_product_by_id
)
from config import COLORS
from datetime import datetime

class OrderWindow(QMainWindow):
    def __init__(self, parent=None, order_id=None):
        super().__init__(parent)
        self.parent_window = parent
        self.order_id = order_id
        self.is_edit = order_id is not None
        self.selected_items = []
        
        self.setWindowTitle("Редактирование заказа" if self.is_edit else "Добавление заказа")
        self.setGeometry(200, 100, 900, 700)
        self.setModal(True)
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {COLORS['main_background']}; }}
            QLabel {{
                font-family: 'Comic Sans MS';
                font-size: 13px;
                color: #333333;
            }}
            QLineEdit, QComboBox, QDateEdit, QSpinBox {{
                font-family: 'Comic Sans MS';
                padding: 8px;
                border: 2px solid {COLORS['secondary_background']};
                border-radius: 6px;
                font-size: 13px;
                background-color: #F8F9FA;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {{
                border-color: {COLORS['accent']};
            }}
            QPushButton {{
                font-family: 'Comic Sans MS';
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                color: white;
            }}
            QPushButton#save {{
                background-color: #28A745;
            }}
            QPushButton#save:hover {{ background-color: #218838; }}
            QPushButton#cancel {{
                background-color: #6C757D;
            }}
            QPushButton#cancel:hover {{ background-color: #5A6268; }}
            QPushButton#add_item {{
                background-color: {COLORS['accent']};
            }}
            QPushButton#add_item:hover {{ background-color: #3D5A7A; }}
            QPushButton#remove_item {{
                background-color: #DC3545;
            }}
            QPushButton#remove_item:hover {{ background-color: #C82333; }}
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
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("✏️ Редактирование заказа" if self.is_edit else "➕ Добавление заказа")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C4360;")
        layout.addWidget(title)
        
        # Информация о заказе
        info_group = QGroupBox("Информация о заказе")
        info_group.setStyleSheet("""
            QGroupBox {
                font-family: 'Comic Sans MS';
                font-weight: bold;
                border: 2px solid #ABCFCE;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        info_layout = QGridLayout(info_group)
        info_layout.setSpacing(12)
        info_layout.setVerticalSpacing(15)
        
        row = 0
        
        info_layout.addWidget(QLabel("Номер заказа:*"), row, 0)
        self.order_number_input = QLineEdit()
        self.order_number_input.setPlaceholderText("Введите номер заказа")
        info_layout.addWidget(self.order_number_input, row, 1)
        row += 1
        
        info_layout.addWidget(QLabel("Клиент:*"), row, 0)
        self.client_combo = QComboBox()
        self.client_combo.setEditable(True)
        for user in get_all_users():
            if user['role'] == 'Авторизированный клиент':
                self.client_combo.addItem(user['full_name'], user['id'])
        info_layout.addWidget(self.client_combo, row, 1)
        row += 1
        
        info_layout.addWidget(QLabel("Пункт выдачи:*"), row, 0)
        self.pickup_combo = QComboBox()
        for point in get_all_pickup_points():
            self.pickup_combo.addItem(point['address'], point['id'])
        info_layout.addWidget(self.pickup_combo, row, 1)
        row += 1
        
        info_layout.addWidget(QLabel("Дата заказа:*"), row, 0)
        self.order_date_edit = QDateEdit()
        self.order_date_edit.setCalendarPopup(True)
        self.order_date_edit.setDate(QDate.currentDate())
        info_layout.addWidget(self.order_date_edit, row, 1)
        row += 1
        
        info_layout.addWidget(QLabel("Дата доставки:"), row, 0)
        self.delivery_date_edit = QDateEdit()
        self.delivery_date_edit.setCalendarPopup(True)
        self.delivery_date_edit.setDate(QDate.currentDate().addDays(7))
        info_layout.addWidget(self.delivery_date_edit, row, 1)
        row += 1
        
        info_layout.addWidget(QLabel("Код получения:*"), row, 0)
        self.pickup_code_input = QLineEdit()
        self.pickup_code_input.setPlaceholderText("Введите код для получения")
        info_layout.addWidget(self.pickup_code_input, row, 1)
        row += 1
        
        info_layout.addWidget(QLabel("Статус:*"), row, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Новый", "Завершен"])
        info_layout.addWidget(self.status_combo, row, 1)
        row += 1
        
        layout.addWidget(info_group)
        
        # Товары в заказе
        items_group = QGroupBox("Товары в заказе")
        items_group.setStyleSheet("""
            QGroupBox {
                font-family: 'Comic Sans MS';
                font-weight: bold;
                border: 2px solid #ABCFCE;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        items_layout = QVBoxLayout(items_group)
        
        btn_layout = QHBoxLayout()
        add_item_btn = QPushButton("➕ Добавить товар")
        add_item_btn.setObjectName("add_item")
        add_item_btn.clicked.connect(self.add_item)
        btn_layout.addWidget(add_item_btn)
        
        remove_item_btn = QPushButton("🗑 Удалить выбранный товар")
        remove_item_btn.setObjectName("remove_item")
        remove_item_btn.clicked.connect(self.remove_item)
        btn_layout.addWidget(remove_item_btn)
        btn_layout.addStretch()
        items_layout.addLayout(btn_layout)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels([
            "Артикул", "Наименование товара", "Цена", "Количество"
        ])
        self.items_table.setAlternatingRowColors(True)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.items_table.horizontalHeader().setStretchLastSection(True)
        items_layout.addWidget(self.items_table)
        
        layout.addWidget(items_group)
        
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        self.total_label = QLabel("ИТОГО: 0 ₽")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2C4360;")
        total_layout.addWidget(self.total_label)
        layout.addLayout(total_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("💾 Сохранить заказ")
        save_btn.setObjectName("save")
        save_btn.clicked.connect(self.save_order)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setObjectName("cancel")
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        if self.is_edit:
            self.load_order_data()
    
    def load_order_data(self):
        order = get_order_by_id(self.order_id)
        if not order:
            QMessageBox.critical(self, "Ошибка", "Заказ не найден")
            self.close()
            return
        
        self.order_number_input.setText(str(order['order_number']))
        self.order_number_input.setReadOnly(True)
        
        for i in range(self.client_combo.count()):
            if self.client_combo.itemData(i) == order['user_id']:
                self.client_combo.setCurrentIndex(i)
                break
        
        for i in range(self.pickup_combo.count()):
            if self.pickup_combo.itemData(i) == order['pickup_point_id']:
                self.pickup_combo.setCurrentIndex(i)
                break
        
        if order['order_date']:
            date = QDate.fromString(order['order_date'], "yyyy-MM-dd")
            self.order_date_edit.setDate(date)
        
        if order['delivery_date']:
            date = QDate.fromString(order['delivery_date'], "yyyy-MM-dd")
            self.delivery_date_edit.setDate(date)
        
        self.pickup_code_input.setText(order['pickup_code'])
        self.status_combo.setCurrentText(order['status'])
        
        items = get_order_items(self.order_id)
        self.selected_items = []
        for item in items:
            self.selected_items.append({
                'product_id': item['product_id'],
                'quantity': item['quantity']
            })
        
        self.update_items_table()
    
    def add_item(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить товар")
        dialog.setFixedSize(400, 200)
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Выберите товар:"))
        product_combo = QComboBox()
        products = get_all_products()
        for p in products:
            product_combo.addItem(f"{p['article']} - {p['name']} ({p['price']} ₽)", p['id'])
        layout.addWidget(product_combo)
        
        layout.addWidget(QLabel("Количество:"))
        quantity_spin = QSpinBox()
        quantity_spin.setMinimum(1)
        quantity_spin.setMaximum(999)
        quantity_spin.setValue(1)
        layout.addWidget(quantity_spin)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("Добавить")
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-family: 'Comic Sans MS';
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #3D5A7A; }}
        """)
        ok_btn.clicked.connect(lambda: self.confirm_add_item(dialog, product_combo, quantity_spin))
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-family: 'Comic Sans MS';
                font-size: 13px;
            }
            QPushButton:hover { background-color: #5A6268; }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        dialog.exec_()
    
    def confirm_add_item(self, dialog, product_combo, quantity_spin):
        product_id = product_combo.currentData()
        quantity = quantity_spin.value()
        
        for item in self.selected_items:
            if item['product_id'] == product_id:
                QMessageBox.warning(
                    self, 
                    "Внимание", 
                    "Этот товар уже добавлен в заказ."
                )
                dialog.reject()
                return
        
        self.selected_items.append({
            'product_id': product_id,
            'quantity': quantity
        })
        
        self.update_items_table()
        dialog.accept()
    
    def remove_item(self):
        current_row = self.items_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите товар для удаления")
            return
        
        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            'Удалить этот товар из заказа?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.selected_items[current_row]
            self.update_items_table()
    
    def update_items_table(self):
        self.items_table.setRowCount(len(self.selected_items))
        total = 0
        
        for i, item in enumerate(self.selected_items):
            product = get_product_by_id(item['product_id'])
            if product:
                price = product['price'] * (1 - product['discount'] / 100)
                total += price * item['quantity']
                
                self.items_table.setItem(i, 0, QTableWidgetItem(product['article']))
                self.items_table.setItem(i, 1, QTableWidgetItem(product['name']))
                self.items_table.setItem(i, 2, QTableWidgetItem(f"{price:.2f} ₽"))
                self.items_table.setItem(i, 3, QTableWidgetItem(str(item['quantity'])))
        
        self.total_label.setText(f"ИТОГО: {total:.2f} ₽")
    
    def save_order(self):
        """Сохранение заказа"""
        try:
            # Проверка обязательных полей
            if not self.order_number_input.text().strip():
                QMessageBox.warning(self, "Ошибка", "Введите номер заказа")
                return
            
            if self.client_combo.currentIndex() < 0:
                QMessageBox.warning(self, "Ошибка", "Выберите клиента")
                return
            
            if self.pickup_combo.currentIndex() < 0:
                QMessageBox.warning(self, "Ошибка", "Выберите пункт выдачи")
                return
            
            if not self.pickup_code_input.text().strip():
                QMessageBox.warning(self, "Ошибка", "Введите код получения")
                return
            
            if not self.selected_items:
                QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один товар в заказ")
                return
            
            # Собираем данные
            order_data = {
                'order_number': int(self.order_number_input.text().strip()),
                'user_id': self.client_combo.currentData(),
                'pickup_point_id': self.pickup_combo.currentData(),
                'order_date': self.order_date_edit.date().toString("yyyy-MM-dd"),
                'delivery_date': self.delivery_date_edit.date().toString("yyyy-MM-dd"),
                'pickup_code': self.pickup_code_input.text().strip(),
                'status': self.status_combo.currentText()
            }
            
            items = [{'product_id': item['product_id'], 'quantity': item['quantity']} for item in self.selected_items]
            
            # Сохраняем
            if self.is_edit:
                update_order(self.order_id, order_data, items)
                QMessageBox.information(self, "Успех", "Заказ обновлён")
            else:
                add_order(order_data, items)
                QMessageBox.information(self, "Успех", "Заказ добавлен")
            
            # Обновляем таблицу в главном окне
            if self.parent_window:
                # Обновляем товары
                if hasattr(self.parent_window, 'load_products'):
                    self.parent_window.load_products()
                
                # Обновляем заказы
                if hasattr(self.parent_window, 'load_orders'):
                    self.parent_window.load_orders()
            
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")