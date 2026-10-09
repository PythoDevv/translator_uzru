from environs import Env

# environs kutubxonasidan foydalanish
env = Env()
env.read_env()

# .env fayl ichidan quyidagilarni o'qiymiz
BOT_TOKEN = env.str("BOT_TOKEN")  # Bot toekn
ADMINS = [int(admin) for admin in env.list(
    "ADMINS", default=["1033990411", "935795577", "1604052132"]
)]
# Tarjimalar Gemini API orqali bajariladi. Modelni .env orqali almashtirish
# mumkin, ammo odatda standart qiymatni o'zgartirish shart emas.
GEMINI_API_KEY = env.str("GEMINI_API_KEY", default="")
# Eski .env dagi nom ham vaqtincha qo'llab-quvvatlanadi. Yangi loyihalarda
# GEMINI_FALLBACK_API_KEY nomidan foydalanish kerak.
GEMINI_FALLBACK_API_KEY = env.str(
    "GEMINI_FALLBACK_API_KEY",
    default=env.str("Ehtiyotshart_api_key", default=""),
)
GEMINI_API_KEYS = tuple(dict.fromkeys(
    key for key in (GEMINI_API_KEY, GEMINI_FALLBACK_API_KEY) if key
))
GEMINI_MODEL = env.str("GEMINI_MODEL", default="gemini-3.1-flash-lite")
IP = env.str("ip")  # Xosting ip manzili

DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")
