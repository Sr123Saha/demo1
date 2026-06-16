
# ui/login_window.py
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import get_user_by_login_password
from config import COLORS, RESOURCES_DIR

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в систему - ЧитайГород")
        self.setFixedSize(500, 500)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['main_background']};
            }}
            QLabel {{
                font-family: 'Comic Sans MS';
                font-size: 14px;
                color: #333333;
            }}
            QLineEdit {{
                font-family: 'Comic Sans MS';
                padding: 12px;
                border: 2px solid {COLORS['secondary_background']};
                border-radius: 8px;
                font-size: 14px;
                background-color: #F8F9FA;
                min-height: 20px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
                background-color: white;
            }}
            QPushButton {{
                font-family: 'Comic Sans MS';
                font-size: 15px;
                font-weight: bold;
                padding: 14px;
                border: none;
                border-radius: 8px;
                color: white;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: #3D5A7A;
            }}
            QPushButton:pressed {{
                background-color: #2C4360;
            }}
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 40, 50, 40)
        
        # Логотип
        logo_label = QLabel()
        logo_path = RESOURCES_DIR / "logo.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(pixmap)
                logo_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(logo_label)
        
        # Заголовок
        title = QLabel("📚 Добро пожаловать!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #2C4360; font-family: 'Comic Sans MS';")
        layout.addWidget(title)
        
        subtitle = QLabel("Войдите в систему или продолжайте как гость")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #666666; font-family: 'Comic Sans MS';")
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # Поле логина
        login_label = QLabel("👤 Логин:")
        login_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(login_label)
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите email или логин")
        self.login_input.returnPressed.connect(self.login)
        layout.addWidget(self.login_input)
        
        # Поле пароля
        password_label = QLabel("🔒 Пароль:")
        password_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.login)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(10)
        
        # Кнопка входа
        self.login_btn = QPushButton("🔑 Войти")
        self.login_btn.clicked.connect(self.login)
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                padding: 14px;
                border-radius: 8px;
                font-family: 'Comic Sans MS';
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #3D5A7A;
            }}
        """)
        layout.addWidget(self.login_btn)
        
        # Кнопка "Войти как гость"
        self.guest_btn = QPushButton("👤 Войти как гость")
        self.guest_btn.clicked.connect(self.guest_login)
        self.guest_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary_background']};
                color: #333333;
                border: none;
                padding: 14px;
                border-radius: 8px;
                font-family: 'Comic Sans MS';
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #9BB8C8;
            }}
        """)
        layout.addWidget(self.guest_btn)
        
        # Метка для ошибок
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: red; font-size: 13px; min-height: 30px; font-family: 'Comic Sans MS';")
        layout.addWidget(self.error_label)
        
        layout.addStretch()
    
    def login(self):
        """Обработка авторизации"""
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        
        if not login or not password:
            self.error_label.setText("❌ Пожалуйста, заполните все поля")
            self.error_label.setStyleSheet("color: red; font-size: 13px; min-height: 30px;")
            return
        
        user = get_user_by_login_password(login, password)
        if user:
            self.error_label.setText("✅ Вход выполнен успешно!")
            self.error_label.setStyleSheet("color: green; font-size: 13px; min-height: 30px;")
            self.open_main_window(user)
        else:
            self.error_label.setText("❌ Неверный логин или пароль")
            self.error_label.setStyleSheet("color: red; font-size: 13px; min-height: 30px;")
            self.password_input.clear()
            self.password_input.setFocus()
    
    def guest_login(self):
        """Вход как гость"""
        self.open_main_window(None)
    
    def open_main_window(self, user):
        """Открытие главного окна"""
        from ui.main_window import MainWindow
        self.main_window = MainWindow(user)
        self.main_window.show()
        self.close()