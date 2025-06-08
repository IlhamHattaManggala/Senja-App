from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf

# Import konfigurasi dan modul database
from config import UPLOAD_FOLDER, configClass
from db import mongo, init_mongo

# Inisialisasi Flask App
app = Flask(__name__)
CORS(app)

# Inisialisasi CSRF Protection
csrf = CSRFProtect()
csrf.init_app(app)

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
from controller.AdminController.DataController import add_informasi_lainnya, add_pengguna, add_tari, datas, delete_informasi, delete_taris, edit_informasi, informasi_lainnya, tari_data, tari_edit, update_informasi, update_taris, user_delete, user_edit, user_update
from controller.ForgotPassController import RequestForgotPassword
from controller.LoginController import RequestLogin
from controller.ProfileController.GetProfile import RequestProfile
from controller.VerifyEmailController import RequestVerifyEmail
from controller.ProfileController.UpdateProfile import RequestUpdateProfile
from controller.RegisterController import RequestRegister
from controller.ResetPassController import RequestResetPassword
from controller.RiwayatController import RequestByDate, RequestRiwayat, add_riwayat
from controller.VerifikasiPinController import VerifyPin
from controller.NotifikasiController import deleteNotifikasi, kirim_notifikasi_hari_tari, readNotifikasi, getAllNotifikasi
from controller.ScrappingController import run_scraping 
from controller.VisualisasiController import render_visualizations
from controller.ScrappingController import run_scraping  # Ganti dengan nama file scraping kamu
from controller.LoginGoogleController import LoginGoogle, registerGoogle
from controller.AdminController.AdminBerandaController import admin_beranda
from controller.AdminController.AdminLoginController import admin_check_login, admin_login, admin_logout
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

# Middleware untuk validasi token
from middleware.token import token_required

# Inisialisasi scheduler
scheduler = BackgroundScheduler()

# Scheduler untuk Hari Tari Sedunia setiap tahun pada tanggal 29 April, jam 00:00
trigger_hari_tari = CronTrigger(month=4, day=29, hour=0, minute=0)  # Setiap tanggal 29 April jam 00:00
scheduler.add_job(kirim_notifikasi_hari_tari, trigger_hari_tari, id='hari_tari_job', replace_existing=True)

# Scheduler kedua: Menjadwalkan scraping setiap hari jam 1 AM
trigger_scraping = CronTrigger(hour=1, minute=0)  # Setiap jam 01:00 AM
scheduler.add_job(run_scraping, trigger_scraping, id='scraping_job', replace_existing=True)

scheduler.start()

# Agar job berhenti dengan rapi saat aplikasi ditutup
atexit.register(lambda: scheduler.shutdown())
# ---------------------- Konfigurasi Upload Folder ----------------------
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ---------------------- Basic Authentication ----------------------

user_collection = configClass.USER_COLLECTION
@auth.verify_password
def verify_password(email, password):
    user = mongo.db[user_collection].find_one({'email': email})
    if user and check_password_hash(user['password'], password):
        return user  # Kembalikan objek user agar bisa diakses di route
    return None

# ---------------------- API Key Middleware ----------------------
def check_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')  # Mengambil API Key dari header
        if api_key != app.config['API_KEY']:  # Memeriksa apakah API Key sesuai
            return jsonify({"message": "Unauthorized"}), 401  # Menolak jika tidak valid
        return func(*args, **kwargs)  
    return wrapper

# ---------------------- REGISTER ----------------------
@app.route('/api/users/v1/register', methods=['POST'])
@csrf.exempt
def register():
    return RequestRegister()

# ---------------------- REGISTER Google ----------------------
@app.route('/api/users/v1/register-google', methods=['POST'])
@csrf.exempt
def regisGoogle():
    return registerGoogle()

# ---------------------- LOGIN ----------------------
@app.route('/api/users/v1/login', methods=['POST'])
@csrf.exempt
def login():
    return RequestLogin()

# ---------------------- LOGIN GOOGLE ----------------------
@app.route('/api/users/v1/login-google', methods=['POST'])
@csrf.exempt
def login_google():
    return LoginGoogle()

# -------------------- LOGIN BASIC AUTH ----------------

@app.route('/api/users/v1/login-basic', methods=['POST'])
@auth.login_required
def protected_route():
    user = auth.current_user()
    return jsonify({
        'status': 'success',
        'message': f"Halo {user['name']}, Anda berhasil mengakses endpoint ini!",
        'user': {
            'email': user['email'],
            'role': user['role']
        }
    }), 200

# ---------------------- FORGOT PASSWORD ----------------------
@app.route('/api/users/v1/lupa-password', methods=['POST'])
@csrf.exempt
def forgot_password():
    return RequestForgotPassword()

# ---------------------- VERIFIKASI PIN ----------------------
@app.route('/api/users/v1/verify-pin', methods=['POST'])
@csrf.exempt
def verify_pin():
    return VerifyPin()

# ---------------------- RESET PASSWORD ----------------------
@app.route('/api/users/v1/reset-password', methods=['POST'])
@csrf.exempt
def reset_password():
    return RequestResetPassword()



# ---------------------- BERANDA ----------------------
@app.route('/api/users/v1/verify-email', methods=['POST'])
@csrf.exempt
@token_required
def verifyEmail(current_user):
    return RequestVerifyEmail(current_user)

# ---------------------- BERANDA ----------------------
@app.route('/api/users/v1/beranda', methods=['GET'])
@csrf.exempt
@token_required
def beranda(current_user):
    return RequestBeranda(current_user)

# ------------------------ NOTIFIKASI ---------------------
@app.route('/api/users/v1/notifikasi', methods=['GET'])
@csrf.exempt
@jwt_required()
def list_notifikasi():
    return getAllNotifikasi()

@app.route('/api/users/v1/notifikasi/<string:notif_id>/read', methods=['PATCH'])
@csrf.exempt
def mark_as_read(notif_id):
    return readNotifikasi(notif_id)

@app.route('/api/users/v1/notifikasi/<string:notif_id>', methods=['DELETE'])
@csrf.exempt
def remove_notifikasi(notif_id):
    return deleteNotifikasi(notif_id)

# ---------------------- ROUTE: PROFILE ----------------------
@app.route('/api/users/v1/profile', methods=['GET'])
@csrf.exempt
@token_required
def get_profile(current_user):
    return RequestProfile(current_user)

# ---------------------- ROUTE: UPDATE PROFILE ----------------------
@app.route('/api/users/v1/profile', methods=['PUT'])
@csrf.exempt
@token_required
def update_profile(current_user):
    return RequestUpdateProfile(current_user)

# ---------------------- ROUTE: MENGAMBIL RIWAYAT ----------------------
@app.route('/api/users/v1/riwayat', methods=['GET'])
@csrf.exempt
@token_required
def get_riwayat(current_user):
    return RequestRiwayat(current_user)

# ---------------------- ROUTE: POST RIWAYAT ----------------------
@app.route('/api/users/v1/add-riwayat', methods=['POST'])
@csrf.exempt
@token_required
def addRiwayat(current_user):
    return add_riwayat(current_user)

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

# ---------------------- HALAMAN ADMIN ----------------------
# ======================
# Beranda publik
# ======================
@app.route('/')
def home():
    return render_template('index.html')

# ======================
# Login Admin API
# ======================
@app.route('/api/admin/v1/login', methods=['POST'])
def login_admin():
    return admin_login()

# ======================
# HTML Login Page
# ======================
@app.route('/login-admin.html')
def admins_login():
    return admin_check_login()

# ======================
# Logout
# ======================
@app.route('/logout-admin')
def logout():
    return admin_logout()

# ======================
# Admin Pages (harus login)
# ======================
@app.route('/beranda-admin.html')
def beranda_admin():
    return admin_beranda()

@app.route('/data-pengguna.html')
def data_pengguna():
    return datas()

@app.route('/data-tari.html')
def data_tari():
    return tari_data()

@app.route('/data-informasi-lainnya.html')
def data_informasi_lainnya():
    return informasi_lainnya()

#INFORMASI LAINNYA ADMIN
@app.route('/edit-informasi-lainnya/<string:item_id>', methods=['GET'])
def edit_informasi_lainnya(item_id):
    return edit_informasi(item_id)

@app.route('/update-informasi-lainnya/<string:item_id>', methods=['POST'])
def update_informasi_lainnya(item_id):
    return update_informasi(item_id)

@app.route('/delete-informasi-lainnya/<string:item_id>', methods=['POST'])
def delete_informasi_lainnya(item_id):
    return delete_informasi(item_id)

#TARI ADMIN
@app.route('/edit-tari/<string:tari_id>', methods=['GET'])
def edit_tari(tari_id):
    return tari_edit(tari_id)

@app.route('/update-tari/<string:tari_id>', methods=['POST'])
def update_tari(tari_id):
    return update_taris(tari_id)

@app.route('/delete-tari/<string:tari_id>', methods=['POST'])
def delete_tari(tari_id):
    return delete_taris(tari_id)

#Data user
@app.route('/edit-user/<string:user_id>', methods=['GET'])
def edit_user(user_id):
    return user_edit(user_id)

@app.route('/update-user/<string:user_id>', methods=['POST'])
def update_user(user_id):
    return user_update(user_id)

@app.route('/delete-user/<string:user_id>', methods=['POST'])
def delete_user(user_id):
    return user_delete(user_id)

@app.route('/add-pengguna', methods=['GET', 'POST'])
def tambah_pengguna():
    return add_pengguna()

@app.route('/add-tari', methods=['GET', 'POST'])
def tambah_tari():
    return add_tari()

@app.route('/add-informasi-lainnya', methods=['GET', 'POST'])
def tambah_informasi_lainnya():
    return add_informasi_lainnya()


# ---------------------- RUN ----------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0', use_reloader=False)