from flask import request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from db import mongo
from config import configClass
from datetime import timedelta

user_collection = mongo.db[configClass.USER_COLLECTION]
verify_collection = mongo.db[configClass.VERIFY_EMAIL_COLLECTION]

def RequestLogin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    client_api_key = request.headers.get('x-api-key')

    if not client_api_key or client_api_key != configClass.API_KEY:
        return jsonify({
            "status": "Gagal",
            "message": "API key tidak valid"
        }), 401

    # Cari user berdasarkan email
    user = user_collection.find_one({'email': email})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'pesan': 'Email atau password salah'}), 401

    user_id = str(user['_id'])

    # Cek apakah user sudah verifikasi email
    verify_entry = verify_collection.find_one({'user_id': user_id})
    if not verify_entry or verify_entry.get('emailVerifyAt') is None:
        return jsonify({
            'status': 'Gagal',
            'pesan': 'Akun belum diverifikasi. Silakan cek email Anda untuk verifikasi.'
        }), 403

    # Jika sudah verifikasi, buat token
    access_token = create_access_token(
        identity=user_id,
        expires_delta=timedelta(days=1)
    )

    return jsonify({
        'status': 'sukses',
        'pesan': 'Login berhasil',
        'data': {
            'user': {
                'id': user_id,
                'name': user['name'],
                'email': user['email'],
                'role': user['role'],
                'avatar': user['avatar']
            },
            'token': access_token
        }
    }), 200
