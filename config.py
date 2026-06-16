import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
RESOURCES_DIR = BASE_DIR / "resources"
IMAGES_DIR = BASE_DIR / "images"

RESOURCES_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

DB_PATH = BASE_DIR / "database.db"

MAX_IMAGE_WIDTH = 300
MAX_IMAGE_HEIGHT = 200
DEFAULT_IMAGE = "picture.png"

COLORS = {
    "main_background": "#FFFFFF",
    "secondary_background": "#ABCFCE",
    "accent": "#546F94",
    "discount_highlight": "#23E1EF",
    "error": "#FF0000",
    "disabled": "#808080"
}

ROLES = {
    "admin": "Администратор",
    "manager": "Менеджер",
    "client": "Авторизированный клиент",
    "guest": "Гость"
}