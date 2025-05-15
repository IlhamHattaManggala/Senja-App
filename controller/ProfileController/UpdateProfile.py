from flask import request, jsonify
from db import mongo
from bson import ObjectId
from config import ConfigClass, configClass
from werkzeug.security import generate_password_hash

user_collection = mongo.db[ConfigClass.USER_COLLECTION]

def RequestUpdateProfile(current_user):
    update_data = request.get_json()
    client_api_key = request.headers.get('x-api-key')
    if not client_api_key or client_api_key != ConfigClass.API_KEY:
        return jsonify({
            "status": "Gagal",
            "message": "API key tidak valid"
        }), 401

    # Data yang ingin diperbarui
    name = update_data.get('name')
    email = update_data.get('email')
    avatar = update_data.get('avatar')
    password = update_data.get('password')
    role = update_data.get('role')  # Ambil role baru jika ada, ganti dari 'user' menjadi 'role'

    # Validasi bahwa setidaknya satu data perlu diperbarui
    if not name and not email and not avatar and not role:
        return jsonify({'status': 'gagal', 'pesan': 'Minimal satu data harus diupdate'}), 400

    # Jika email diubah, cek apakah email sudah digunakan oleh pengguna lain
    if email and user_collection.find_one({'email': email}):
        return jsonify({'status': 'gagal', 'pesan': 'Email sudah digunakan oleh pengguna lain'}), 409

    # Update data yang valid
    update_values = {}
    if name:
        update_values['name'] = name
    if email:
        update_values['email'] = email
    if avatar:
        update_values['avatar'] = avatar
    if password:
        update_values['password'] = generate_password_hash(password)
    if role:
        update_values['role'] = role  # Pastikan role diupdate dengan benar

    # Memperbarui data pengguna di MongoDB
    user_collection.update_one({'_id': ObjectId(current_user['_id'])}, {'$set': update_values})
    
    updated_user = user_collection.find_one({'_id': ObjectId(current_user['_id'])})


    return jsonify({
        'status': 'sukses',
        'pesan': 'Profil berhasil diperbarui',
        'data': {
            'name': updated_user['name'],
            'email': updated_user['email'],
            'role': role if role else updated_user['role'], 
            'avatar': updated_user['avatar']
        }
    }), 200
