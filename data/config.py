from environs import Env

# environs kutubxonasidan foydalanish
env = Env()
env.read_env()

# .env fayl ichidan quyidagilarni o'qiymiz
BOT_TOKEN = env.str("BOT_TOKEN")  # Bot toekn
ADMINS = [int(admin) for admin in env.list(
    "ADMINS", default=["1033990411", "935795577", "1604052132"]
)]
# Agar kalit berilsa rasmiy Google Cloud Translation API ishlatiladi.
# Kalitsiz holatda bot Google endpointidan foydalanadi.
GOOGLE_TRANSLATE_API_KEY = env.str("GOOGLE_TRANSLATE_API_KEY", default="")
IP = env.str("ip")  # Xosting ip manzili

DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")
