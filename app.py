from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from flask_httpauth import HTTPBasicAuth  # Import Flask-HTTPAuth

# Import konfigurasi dan modul database
from config import configClass
from db import mongo, init_mongo  # pastikan init_mongo menginisialisasi mongo

# Inisialisasi Flask App
app = Flask(__name__)
CORS(app)

# Inisialisasi BasicAuth
auth = HTTPBasicAuth()

# Inisialisasi JWT
jwt = JWTManager(app)

# Konfigurasi dari config class
app.config.from_object(configClass)

# Inisialisasi MongoDB sebelum mengimpor controller
init_mongo(app)

# Sekarang aman untuk import semua controller (karena mongo sudah siap)
from controller.BerandaController import RequestBeranda
from controller.ForgotPassController import RequestForgotPassword
from controller.LoginController import RequestLogin
from controller.ProfileController.GetProfile import RequestProfile
from controller.ProfileController.UpdateProfile import RequestUpdateProfile
from controller.RegisterController import RequestRegister
from controller.ResetPassController import RequestResetPassword
from controller.RiwayatController import RequestByDate, RequestRiwayat, add_riwayat
from controller.VerifikasiPinController import VerifyPin
from controller.NotifikasiController import deleteNotifikasi, readNotifikasi, getAllNotifikasi
from controller.ScrappingController import run_scraping 
from controller.VisualisasiController import render_visualizations

# Middleware untuk validasi token
from middleware.token import token_required

# ---------------------- Basic Authentication ----------------------
@auth.verify_password
def verify_password(email, password):
    if email in app.config['BASIC_AUTH_USERS'] and app.config['BASIC_AUTH_USERS'][email] == password:
        return email  # Mengembalikan email jika autentikasi berhasil
    return None  # Kembalikan None jika gagal


# ---------------------- API Key Middleware ----------------------
def check_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')  # Mengambil API Key dari header
        if api_key != app.config['API_KEY']:  # Memeriksa apakah API Key sesuai
            return jsonify({"message": "Unauthorized"}), 401  # Menolak jika tidak valid
        return func(*args, **kwargs)  # Lanjutkan ke fungsi jika API Key valid
    return wrapper

# ---------------------- ROUTES ----------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data.html')
def data():
    articles = mongo.db.articles.find()
    return render_template('data.html', articles=articles)

@app.route('/visualisasi')
def visualisasi():
    return render_visualizations() 

# ---------------------- REGISTER ----------------------
@app.route('/api/users/v1/register', methods=['POST'])
def register():
    return RequestRegister()

# ---------------------- LOGIN ----------------------
@app.route('/api/users/v1/login', methods=['POST'])
#@auth.login_required  # Menambahkan Basic Auth ke endpoint login
def login():
    return RequestLogin()

# ---------------------- FORGOT PASSWORD ----------------------
@app.route('/api/users/v1/forgot-password', methods=['POST'])
def forgot_password():
    return RequestForgotPassword()

# ---------------------- VERIFIKASI PIN ----------------------
@app.route('/api/users/v1/verify-pin', methods=['POST'])
def verify_pin():
    return VerifyPin()

# ---------------------- RESET PASSWORD ----------------------
@app.route('/api/users/v1/reset-password', methods=['POST'])
def reset_password():
    return RequestResetPassword()

# ---------------------- BERANDA ----------------------
@app.route('/api/users/v1/beranda', methods=['GET'])
@token_required
def beranda(current_user):
    return RequestBeranda(current_user)

# ------------------------ NOTIFIKASI ---------------------
@app.route('/api/users/v1/notifikasi', methods=['GET'])
@jwt_required()
def list_notifikasi():
    return getAllNotifikasi()

@app.route('/api/users/v1/notifikasi/<string:notif_id>/read', methods=['PATCH'])
def mark_as_read(notif_id):
    return readNotifikasi(notif_id)

@app.route('/api/users/v1/notifikasi/<string:notif_id>', methods=['DELETE'])
def remove_notifikasi(notif_id):
    return deleteNotifikasi(notif_id)

# ---------------------- ROUTE: PROFILE ----------------------
@app.route('/api/users/v1/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return RequestProfile(current_user)

# ---------------------- ROUTE: UPDATE PROFILE ----------------------
@app.route('/api/users/v1/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    return RequestUpdateProfile(current_user)

# ---------------------- ROUTE: MENGAMBIL RIWAYAT ----------------------
@app.route('/api/users/v1/riwayat', methods=['GET'])
@token_required
def get_riwayat(current_user):
    return RequestRiwayat(current_user)

# ---------------------- ROUTE: RUN SCRAPING ----------------------
@app.route('/run_scraping', methods=['GET'])
def start_scraping():
    run_scraping()  # Menjalankan fungsi scraping yang ada di scraper.py
    return "Scraping selesai!"  # Feedback ke pengguna bahwa scraping telah selesai

# ---------------------- ROUTE: ARTICLES ----------------------
@app.route('/api/articles', methods=['GET'])
@check_api_key  # Memeriksa API Key sebelum mengakses data artikel
def get_articles():
    articles = mongo.db[configClass.TARI_ARTICLE_COLLECTION].find()
    result = []
    for article in articles:
        result.append({
            "title": article["title"],
            "url": article["url"],
            "date": article["date"],
            "image_url": article.get("image_url", ""),
            "content": article.get("content", "")
        })
    return jsonify(result)

# ---------------------- RUN ----------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')

