from flask import request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from db import mongo
from config import configClass
def RequestLogin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    api_key = request.headers.get('x-api-key')
    
    if api_key not in configClass.API_KEY:
        return jsonify({'pesan': 'API key tidak valid'}), 403
    
    user_collection = configClass.USER_COLLECTION
    user = mongo.db[user_collection].find_one({'email': email})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'pesan': 'Email atau password salah'}), 401

    access_token = create_access_token(
        identity=str(user['_id']),  # ini akan menjadi claim `sub`
        additional_claims={
            "name": user['name'],
            "email": user['email'],
            "role": user['role'],
            "avatar": user['avatar'],
            "password": user['password']
        }
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