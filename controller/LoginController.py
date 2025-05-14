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
<<<<<<< HEAD

=======
    api_key = request.headers.get('x-api-key')
    
    if api_key not in configClass.API_KEY:
        return jsonify({'pesan': 'API key tidak valid'}), 403
    
>>>>>>> 1a0098daa81f648d48da525b022c826e9c9e7a3d
    user_collection = configClass.USER_COLLECTION
    user = mongo.db[user_collection].find_one({'email': email})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'pesan': 'Email atau password salah'}), 401

    # Token hanya berisi _id, tidak ada data sensitif lainnya
    access_token = create_access_token(
<<<<<<< HEAD
        identity=str(user['_id']),
        expires_delta=timedelta(hours=1)  # Token akan kedaluwarsa dalam 1 jam
=======
        identity=str(user['_id']),  # ini akan menjadi claim `sub`
        additional_claims={
            "name": user['name'],
            "email": user['email'],
            "role": user['role'],
            "avatar": user['avatar'],
            "password": user['password']
        }
>>>>>>> 1a0098daa81f648d48da525b022c826e9c9e7a3d
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
