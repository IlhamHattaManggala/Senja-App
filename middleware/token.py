from functools import wraps
from bson import ObjectId
from flask import request, jsonify
import jwt
from config import ConfigClass  # Mengimpor ConfigClass dari config.py
from flask_jwt_extended import get_jwt_identity, jwt_required, JWTManager
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from db import mongo  # Pastikan mengimpor mongo dari db.py

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'pesan': 'Token tidak ditemukan'}), 401
        try:
            token = token.split(" ")[1]  # Ambil token setelah 'Bearer'
            # Dekode token menggunakan pyjwt.decode() dari pustaka pyjwt
            data = jwt.decode(token, ConfigClass.SECRET_KEY, algorithms=['HS256'])  # Gunakan ConfigClass.SECRET_KEY
            current_user = mongo.db[ConfigClass.USER_COLLECTION].find_one({"_id": ObjectId(data['sub'])})  # Menggunakan koleksi dinamis dari ConfigClass
            if not current_user:
                return jsonify({'pesan': 'User tidak ditemukan'}), 404
        except ExpiredSignatureError:
            return jsonify({'pesan': 'Token expired'}), 401
        except InvalidTokenError:
            return jsonify({'pesan': 'Token invalid'}), 401
        return f(current_user, *args, **kwargs)  # Pass current_user ke route yang memanggilnya
    return decorated
