from flask import Flask
from controller.BerandaController import RequestBeranda
from controller.ForgotPassController import RequestForgotPassword
from controller.LoginController import RequestLogin
from controller.ProfileController.GetProfile import RequestProfile
from controller.ProfileController.UpdateProfile import RequestUpdateProfile
from controller.RegisterController import RequestRegister
from controller.ResetPassController import RequestResetPassword
from controller.RiwayatController import RequestByDate, RequestRiwayat, add_riwayat
from controller.VerifikasiPinController import VerifyPin
from db import mongo, init_mongo
from functools import wraps
from flask_cors import CORS
from flask_jwt_extended import jwt_required, JWTManager
from controller.NotifikasiController import deleteNotifikasi, readNotifikasi, getAllNotifikasi
from config import configClass
from middleware.token import token_required


app = Flask(__name__)
CORS(app)

# Konfigurasi aplikasi
app.config.from_object(configClass)

# Inisialisasi JWT
jwt = JWTManager(app)

# Inisialisasi Mongo
init_mongo(app)

# ---------------------- REGISTER ----------------------
@app.route('/api/users/v1/register', methods=['POST'])
def register():
    return RequestRegister()

# ---------------------- LOGIN ----------------------
@app.route('/api/users/v1/login', methods=['POST'])
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

#------------------------ NOTIFIKASI ---------------------

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
    
# ---------------------- Emang ini kepakai?? -----------------------------
# ---------------------- ROUTE: MENAMBAHKAN RIWAYAT ----------------------
# @app.route('/api/users/v1/riwayat', methods=['POST'])
# @token_required
# def tambahRiwayat(current_user):
#     return add_riwayat(current_user)
# ---------------------- ROUTE: MENGAMBIL RIWAYAT PER TANGGAL ----------------------
# @app.route('/api/users/v1/riwayat/<date>', methods=['GET'])
# @token_required
# def get_riwayat_by_date(current_user, date):
#     return RequestByDate(current_user, date)

# ---------------------- RUN ----------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
