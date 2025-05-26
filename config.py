import os
from werkzeug.utils import secure_filename as werkzeug_secure_filename

MONGO_URI = "mongodb://localhost:27017/senja"
DATABASE_NAME = "senja"
SECRET_KEY = 'senja-app'
USER_COLLECTION = "users"
HISTORY_COLLECTION = "history"
NOTIFIKASI_COLLECTION = "notifikasi"
RESET_PASSWORD_COLLECTION = "reset_password"
TARI_COLLECTION = "tari"
SENI_LAINNYA_COLLECTION = "seni_lainnya"
TARI_ARTICLE_COLLECTION = "tari_article"

# Menambahkan Basic Authentication Users
BASIC_AUTH_USERS = {
    "kelompokcapstone123@gmail.com": "kelompokcapstone123"  
}


# Menambahkan API Key untuk akses API
API_KEY = 'senjawebdev-12'  # Ganti dengan API Key yang aman dan unik
UPLOAD_FOLDER = os.path.join("static", "img", "avatar")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename):
    return werkzeug_secure_filename(filename)
class ConfigClass:
    SECRET_KEY = SECRET_KEY
    MONGO_URI = MONGO_URI
    DATABASE_NAME = DATABASE_NAME
    USER_COLLECTION = USER_COLLECTION
    HISTORY_COLLECTION = HISTORY_COLLECTION
    NOTIFIKASI_COLLECTION = NOTIFIKASI_COLLECTION
    RESET_PASSWORD_COLLECTION = RESET_PASSWORD_COLLECTION
    TARI_COLLECTION = TARI_COLLECTION
    SENI_LAINNYA_COLLECTION = SENI_LAINNYA_COLLECTION
    TARI_ARTICLE_COLLECTION = TARI_ARTICLE_COLLECTION

    JWT_SECRET_KEY = SECRET_KEY  
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer' 
    
    # Flask-Mail configurations
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'ilhamhattamanggala123@gmail.com'  # Ganti dengan email Anda
    MAIL_PASSWORD = 'nxei sqvz guzs yujp'  # Ganti dengan password aplikasi atau password email Anda
    MAIL_DEFAULT_SENDER = 'senjaapp@gmail.com'  # Email pengirim

    # Menambahkan Basic Authentication dan API Key konfigurasi
    BASIC_AUTH_USERS = BASIC_AUTH_USERS
    API_KEY = API_KEY

configClass = ConfigClass()