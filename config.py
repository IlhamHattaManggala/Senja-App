
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
    "aurapita11@gmail.com": "Aurapita111"  # email dan password untuk login
}


# Menambahkan API Key untuk akses API
API_KEY = 'your-api-key-here'  # Ganti dengan API Key yang aman dan unik

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
    MAIL_USERNAME = 'your_email@gmail.com'  # Ganti dengan email Anda
    MAIL_PASSWORD = 'your_password'  # Ganti dengan password aplikasi atau password email Anda
    MAIL_DEFAULT_SENDER = 'your_email@gmail.com'  # Email pengirim

    # Menambahkan Basic Authentication dan API Key konfigurasi
    BASIC_AUTH_USERS = BASIC_AUTH_USERS
    API_KEY = API_KEY

configClass = ConfigClass()
