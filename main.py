# main.py
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from database import init_database
from imports import import_all_data
from ui.login_window import LoginWindow
from config import RESOURCES_DIR

def main():
    init_database()
    # import_all_data()  # Раскомментировано для первого запуска
    
    app = QApplication(sys.argv)
    
    icon_path = RESOURCES_DIR / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    window = LoginWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()