"""
MemeMakerBot - Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# === Paths ===
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = DATA_DIR / "templates"
GENERATED_DIR = DATA_DIR / "generated"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "bot.db"

# Create directories
for d in [DATA_DIR, TEMPLATES_DIR, GENERATED_DIR, UPLOADS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# === Bot ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
# Don't raise error for web-only deployment
# if not BOT_TOKEN:
#     raise ValueError("BOT_TOKEN is required in .env file")

# === Admins ===
ADMIN_IDS: set[int] = set()
admin_ids_str = os.getenv("ADMIN_IDS", "")
if admin_ids_str:
    ADMIN_IDS = {int(x.strip()) for x in admin_ids_str.split(",") if x.strip().isdigit()}

# === Rate Limiting ===
RATE_LIMIT = int(os.getenv("RATE_LIMIT_MESSAGES", "10"))
RATE_LIMIT_MESSAGES = RATE_LIMIT  # Alias
RATE_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
RATE_LIMIT_PERIOD = RATE_PERIOD  # Alias

# === Validation ===
MAX_TEXT_LENGTH = 200
MAX_IMAGE_SIZE_MB = 10
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

# === User Uploads ===
MAX_UPLOADS_PER_DAY = 3  # Limit uploads per user per day
MIN_IMAGE_SIZE = (200, 200)  # Minimum image dimensions
MAX_IMAGE_SIZE = (4096, 4096)  # Maximum image dimensions

# === Pagination ===
TEMPLATES_PER_PAGE = 6

# === Web Platform ===
WEB_URL = os.getenv("WEB_URL", "https://web-production-9a1f5.up.railway.app")

# === Logging ===
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# === Fonts ===
FONT_PATHS = [
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/liberation-fonts/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
