from flask import request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from db import mongo

def RequestLogin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = mongo.db.users.find_one({'email': email})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'pesan': 'Email atau password salah'}), 401

    access_token = create_access_token(
        identity=str(user['_id']),  # ini akan menjadi claim `sub`
        additional_claims={
            "name": user['name'],
            "email": user['email'],
            "role": user['role'],
            "avatar": user['avatar']
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