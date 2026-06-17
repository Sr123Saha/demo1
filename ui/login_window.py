# ui/login_window.py
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from database import get_user_by_login_password
from config import COLORS, RESOURCES_DIR

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в систему - ЧитайГород")
        self.setFixedSize(500, 550)

        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; }
            QLabel {
                font-family: 'Comic Sans MS';
                color: #333333;
            }
            QLineEdit {
                font-family: 'Comic Sans MS';
                padding: 12px;
                border: 2px solid #ABCFCE;
                border-radius: 8px;
                font-size: 14px;
                background-color: #F8F9FA;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #546F94;
                background-color: white;
            }
            QPushButton {
                font-family: 'Comic Sans MS';
                font-size: 15px;
                font-weight: bold;
                padding: 14px;
                border: none;
                border-radius: 8px;
                color: white;
                min-height: 20px;
                background-color: #546F94;
            }
            QPushButton:hover { background-color: #3D5A7A; }
            QPushButton:pressed { background-color: #2C4360; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(50, 30, 50, 30)

        # Логотип
        logo_label = QLabel()
        logo_path = RESOURCES_DIR / "logo.png"
        if not logo_path.exists():
            logo_path = RESOURCES_DIR / "icon.png"

        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(pixmap)
                logo_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(logo_label)

        layout.addSpacing(10)

        # Заголовок
        title = QLabel("Добро пожаловать!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C4360;")
        layout.addWidget(title)

        layout.addSpacing(5)

        subtitle = QLabel("Войдите в систему или продолжайте как гость")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #888888;")
        layout.addWidget(subtitle)

        layout.addSpacing(25)

        # Логин
        login_label = QLabel("Логин")
        login_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #555555;")
        layout.addWidget(login_label)

        layout.addSpacing(5)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите email или логин")
        self.login_input.setMinimumHeight(40)
        self.login_input.returnPressed.connect(self.login)
        layout.addWidget(self.login_input)

        layout.addSpacing(18)

        # Пароль
        password_label = QLabel("Пароль")
        password_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #555555;")
        layout.addWidget(password_label)

        layout.addSpacing(5)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setMinimumHeight(40)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.login)
        layout.addWidget(self.password_input)

        layout.addSpacing(25)

        # Кнопка входа
        self.login_btn = QPushButton("Войти")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)

        layout.addSpacing(10)

        # Кнопка гостя
        self.guest_btn = QPushButton("Войти как гость")
        self.guest_btn.setMinimumHeight(45)
        self.guest_btn.clicked.connect(self.guest_login)
        self.guest_btn.setStyleSheet("""
            QPushButton {
                background-color: #ABCFCE;
                color: #333333;
                font-family: 'Comic Sans MS';
                font-size: 15px;
                font-weight: bold;
                padding: 14px;
                border: none;
                border-radius: 8px;
                min-height: 20px;
            }
            QPushButton:hover { background-color: #9BB8C8; }
            QPushButton:pressed { background-color: #8AA8B8; }
        """)
        layout.addWidget(self.guest_btn)

        layout.addSpacing(15)

        # Ошибки
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setMinimumHeight(30)
        self.error_label.setStyleSheet("color: red; font-size: 13px;")
        layout.addWidget(self.error_label)

        layout.addStretch()

    def login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not login or not password:
            self.error_label.setText("Заполните все поля")
            self.error_label.setStyleSheet("color: red; font-size: 13px;")
            return

        user = get_user_by_login_password(login, password)
        if user:
            self.error_label.setText("Вход выполнен успешно!")
            self.error_label.setStyleSheet("color: green; font-size: 13px;")
            from ui.main_window import MainWindow
            self.main_window = MainWindow(user)
            self.main_window.show()
            self.close()
        else:
            self.error_label.setText("Неверный логин или пароль")
            self.error_label.setStyleSheet("color: red; font-size: 13px;")
            self.password_input.clear()
            self.password_input.setFocus()

    def guest_login(self):
        self.error_label.setText("Вход как гость")
        self.error_label.setStyleSheet("color: blue; font-size: 13px;")
        from ui.main_window import MainWindow
        self.main_window = MainWindow(None)
        self.main_window.show()
        self.close()