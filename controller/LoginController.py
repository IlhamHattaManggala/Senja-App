from flask import request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from db import mongo
from config import configClass
from datetime import timedelta

def RequestLogin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user_collection = configClass.USER_COLLECTION
    user = mongo.db[user_collection].find_one({'email': email})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'pesan': 'Email atau password salah'}), 401

    # Token hanya berisi _id, tidak ada data sensitif lainnya
    access_token = create_access_token(
        identity=str(user['_id']),
        expires_delta=timedelta(hours=1)  # Token akan kedaluwarsa dalam 1 jam
    )

    return jsonify({
        'status': 'sukses',
        'pesan': 'Login berhasil',
        'data': {
            'user': {
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email'],
                'role': user['role'],
                'avatar': user['avatar']
            },
            'token': access_token
        }
    }), 200
