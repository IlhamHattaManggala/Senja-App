import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename as werkzeug_secure_filename

load_dotenv()  # load dari file .env

class ConfigClass:
    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_NAME = "senja"

    USER_COLLECTION = "users"
    HISTORY_COLLECTION = "history"
    NOTIFIKASI_COLLECTION = "notifikasi"
    RESET_PASSWORD_COLLECTION = "reset_password"
    TARI_COLLECTION = "tari"
    SENI_LAINNYA_COLLECTION = "seni_lainnya"
    TARI_ARTICLE_COLLECTION = "tari_article"
    VERIFY_EMAIL_COLLECTION = "verify_email"
    LOG_ACTIVITY_COLLECTION = "log_activity"

    JWT_SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    BASIC_AUTH_USERS = {
        os.getenv("MAIL_USERNAME"): os.getenv("MAIL_PASSWORD")
    }

    API_KEY = os.getenv("API_KEY")

UPLOAD_FOLDER = os.path.join("static", "img", "avatar")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename):
    return werkzeug_secure_filename(filename)

configClass = ConfigClass()