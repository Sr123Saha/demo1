# ui/product_window.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import (
    get_product_by_article, add_product, update_product,
    get_product_categories, get_product_suppliers
)
from config import COLORS, IMAGES_DIR, RESOURCES_DIR, MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT
from PIL import Image
import os
import shutil

class ProductWindow(QMainWindow):
    def __init__(self, parent=None, article=None):
        super().__init__(parent)
        self.parent_window = parent
        self.article = article
        self.is_edit = article is not None
        self.current_image_path = None
        self.image_filename = None
        
        self.setWindowTitle("Редактирование товара" if self.is_edit else "Добавление товара")
        self.setFixedSize(700, 700)
        self.setWindowModality(Qt.ApplicationModal)  # <-- ИСПРАВЛЕНО!
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {COLORS['main_background']}; }}
            QLabel {{
                font-family: 'Comic Sans MS';
                font-size: 13px;
                color: #333333;
            }}
            QLineEdit, QTextEdit, QComboBox {{
                font-family: 'Comic Sans MS';
                padding: 8px;
                border: 2px solid {COLORS['secondary_background']};
                border-radius: 6px;
                font-size: 13px;
                background-color: #F8F9FA;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
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
            QPushButton#upload {{
                background-color: {COLORS['accent']};
            }}
            QPushButton#upload:hover {{ background-color: #3D5A7A; }}
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("✏️ Редактирование товара" if self.is_edit else "➕ Добавление товара")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C4360;")
        layout.addWidget(title)
        
        # Форма в виде сетки
        form_layout = QGridLayout()
        form_layout.setSpacing(12)
        form_layout.setVerticalSpacing(15)
        
        row = 0
        
        # Артикул
        form_layout.addWidget(QLabel("Артикул:"), row, 0)
        self.article_input = QLineEdit()
        self.article_input.setPlaceholderText("Введите артикул")
        if self.is_edit:
            self.article_input.setReadOnly(True)
        form_layout.addWidget(self.article_input, row, 1)
        row += 1
        
        # Наименование
        form_layout.addWidget(QLabel("Наименование:*"), row, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название товара")
        form_layout.addWidget(self.name_input, row, 1)
        row += 1
        
        # Категория
        form_layout.addWidget(QLabel("Категория:*"), row, 0)
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        for cat in get_product_categories():
            self.category_combo.addItem(cat)
        form_layout.addWidget(self.category_combo, row, 1)
        row += 1
        
        # Описание
        form_layout.addWidget(QLabel("Описание:"), row, 0)
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        form_layout.addWidget(self.desc_input, row, 1)
        row += 1
        
        # Производитель
        form_layout.addWidget(QLabel("Производитель:*"), row, 0)
        self.manufacturer_input = QLineEdit()
        self.manufacturer_input.setPlaceholderText("Введите производителя")
        form_layout.addWidget(self.manufacturer_input, row, 1)
        row += 1
        
        # Поставщик
        form_layout.addWidget(QLabel("Поставщик:*"), row, 0)
        self.supplier_combo = QComboBox()
        self.supplier_combo.setEditable(True)
        for sup in get_product_suppliers():
            self.supplier_combo.addItem(sup)
        form_layout.addWidget(self.supplier_combo, row, 1)
        row += 1
        
        # Цена
        form_layout.addWidget(QLabel("Цена (₽):*"), row, 0)
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        form_layout.addWidget(self.price_input, row, 1)
        row += 1
        
        # Единица измерения
        form_layout.addWidget(QLabel("Ед. измерения:"), row, 0)
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("шт., кг, м...")
        self.unit_input.setText("шт.")
        form_layout.addWidget(self.unit_input, row, 1)
        row += 1
        
        # Количество
        form_layout.addWidget(QLabel("Количество:*"), row, 0)
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("0")
        form_layout.addWidget(self.quantity_input, row, 1)
        row += 1
        
        # Скидка
        form_layout.addWidget(QLabel("Скидка (%):"), row, 0)
        self.discount_input = QLineEdit()
        self.discount_input.setPlaceholderText("0-100")
        self.discount_input.setText("0")
        form_layout.addWidget(self.discount_input, row, 1)
        row += 1
        
        # Фото
        form_layout.addWidget(QLabel("Фото товара:"), row, 0)
        photo_layout = QHBoxLayout()
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(150, 100)
        self.photo_label.setStyleSheet("border: 2px dashed #ABCFCE; border-radius: 6px;")
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setText("🖼️ Нет фото")
        photo_layout.addWidget(self.photo_label)
        
        self.upload_btn = QPushButton("📁 Загрузить")
        self.upload_btn.setObjectName("upload")
        self.upload_btn.clicked.connect(self.upload_image)
        photo_layout.addWidget(self.upload_btn)
        photo_layout.addStretch()
        form_layout.addLayout(photo_layout, row, 1)
        row += 1
        
        layout.addLayout(form_layout)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("💾 Сохранить")
        save_btn.setObjectName("save")
        save_btn.clicked.connect(self.save_product)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setObjectName("cancel")
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        if self.is_edit:
            self.load_product_data()
    
    def load_product_data(self):
        product = get_product_by_article(self.article)
        if not product:
            QMessageBox.critical(self, "Ошибка", "Товар не найден")
            self.close()
            return
        
        self.article_input.setText(product['article'])
        self.name_input.setText(product['name'])
        self.category_combo.setCurrentText(product['category'])
        self.desc_input.setText(product['description'] or '')
        self.manufacturer_input.setText(product['manufacturer'])
        self.supplier_combo.setCurrentText(product['supplier'])
        self.price_input.setText(str(product['price']))
        self.unit_input.setText(product['unit'])
        self.quantity_input.setText(str(product['quantity']))
        self.discount_input.setText(str(product['discount']))
        
        if product['image_path'] and os.path.exists(str(IMAGES_DIR / product['image_path'])):
            self.load_image_to_label(str(IMAGES_DIR / product['image_path']))
            self.image_filename = product['image_path']
    
    def load_image_to_label(self, image_path):
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.photo_label.setPixmap(pixmap)
                self.photo_label.setText("")
        except Exception as e:
            print(f"Ошибка загрузки фото: {e}")
    
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if not file_path:
            return
        
        try:
            with Image.open(file_path) as img:
                img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.Resampling.LANCZOS)
                new_img = Image.new('RGB', (MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), (255, 255, 255))
                x = (MAX_IMAGE_WIDTH - img.width) // 2
                y = (MAX_IMAGE_HEIGHT - img.height) // 2
                new_img.paste(img, (x, y))
                
                filename = f"product_{hash(file_path)}.jpg"
                target_path = IMAGES_DIR / filename
                new_img.save(target_path, 'JPEG', quality=85)
                
                self.image_filename = filename
                self.load_image_to_label(str(target_path))
                QMessageBox.information(self, "Успех", "Изображение загружено")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обработать изображение: {e}")
    
    def save_product(self):
        try:
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Ошибка", "Введите наименование товара")
                return
            
            if not self.category_combo.currentText().strip():
                QMessageBox.warning(self, "Ошибка", "Выберите категорию")
                return
            
            if not self.manufacturer_input.text().strip():
                QMessageBox.warning(self, "Ошибка", "Введите производителя")
                return
            
            if not self.supplier_combo.currentText().strip():
                QMessageBox.warning(self, "Ошибка", "Выберите поставщика")
                return
            
            try:
                price = float(self.price_input.text().strip().replace(',', '.'))
                if price < 0:
                    QMessageBox.warning(self, "Ошибка", "Цена не может быть отрицательной")
                    return
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректную цену (например: 199.99)")
                return
            
            try:
                quantity = int(self.quantity_input.text().strip())
                if quantity < 0:
                    QMessageBox.warning(self, "Ошибка", "Количество не может быть отрицательным")
                    return
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректное количество")
                return
            
            try:
                discount = int(self.discount_input.text().strip() or '0')
                if discount < 0 or discount > 100:
                    QMessageBox.warning(self, "Ошибка", "Скидка должна быть от 0 до 100")
                    return
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректную скидку")
                return
            
            product_data = {
                'article': self.article_input.text().strip(),
                'name': self.name_input.text().strip(),
                'category': self.category_combo.currentText().strip(),
                'description': self.desc_input.toPlainText().strip(),
                'manufacturer': self.manufacturer_input.text().strip(),
                'supplier': self.supplier_combo.currentText().strip(),
                'price': price,
                'unit': self.unit_input.text().strip() or 'шт.',
                'quantity': quantity,
                'discount': discount,
                'image_path': self.image_filename or ''
            }
            
            if self.is_edit:
                product = get_product_by_article(self.article)
                update_product(product['id'], product_data)
                QMessageBox.information(self, "Успех", "Товар обновлён")
            else:
                if get_product_by_article(product_data['article']):
                    QMessageBox.warning(self, "Ошибка", "Товар с таким артикулом уже существует")
                    return
                add_product(product_data)
                QMessageBox.information(self, "Успех", "Товар добавлен")
            
            if self.parent_window:
                self.parent_window.load_products()
            
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")