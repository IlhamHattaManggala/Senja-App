# controller/AdminController/RegisterAdminController.py

from flask import request, jsonify
from werkzeug.security import generate_password_hash
from db import mongo
from config import configClass
from controller.LogActivityController import simpan_log

user_collection = mongo.db[configClass.USER_COLLECTION]

def registerAdmin():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Validasi field kosong
    if not all([name, email, password]):
        return jsonify({'status': 'fail', 'pesan': 'Semua field harus diisi'}), 400

    # Cek apakah email sudah ada
    existing_user = user_collection.find_one({'email': email})
    if existing_user:
        return jsonify({'status': 'fail', 'pesan': 'Email sudah digunakan'}), 400

    # Simpan admin baru
    hashed_password = generate_password_hash(password)
    user = {
        'name': name,
        'email': email,
        'password': hashed_password,
        'role': 'admin',
        'avatar': 'default.jpg'  # atau kamu bisa custom sesuai input
    }

    user_collection.insert_one(user)

    simpan_log(str(user['_id']), email, "Registrasi admin baru")

    return jsonify({'status': 'success', 'pesan': 'Admin berhasil didaftarkan'}), 201