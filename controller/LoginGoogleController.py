from datetime import timedelta
import hashlib
import secrets
import os
import requests
from flask import jsonify, request
from firebase_admin import auth
from flask_jwt_extended import create_access_token
from werkzeug.utils import secure_filename
from config import ConfigClass
from db import mongo

# Fungsi hash MD5
def md5_hash(password):
    return hashlib.md5(password.encode()).hexdigest()

# Fungsi download avatar ke folder static/img/avatar/
def download_avatar(avatar_url, username):
    try:
        if not avatar_url:
            return None

        filename = secure_filename(username.lower().replace(" ", "_")) + ".jpg"
        folder_path = os.path.join("static", "img", "avatar")
        os.makedirs(folder_path, exist_ok=True)
        filepath = os.path.join(folder_path, filename)

        response = requests.get(avatar_url)
        if response.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(response.content)
            return f"/static/img/avatar/{filename}"
        else:
            return None
    except Exception as e:
        print(f"Gagal download avatar: {e}")
        return None

# Fungsi utama login Google
def LoginGoogle():
    try:
        data = request.get_json(force=True)
        client_api_key = request.headers.get('x-api-key')
        if not client_api_key or client_api_key != ConfigClass.API_KEY:
            return jsonify({
                "status": "Gagal",
                "message": "API key tidak valid"
            }), 401

        id_token = data.get('idToken')
        if not id_token:
            return jsonify({'status': 'error', 'message': 'Token is missing'}), 402

        # Verifikasi token dari Firebase
        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token.get('email')
        nama = decoded_token.get('name') or 'User'
        avatar_url = decoded_token.get('picture')

        user_col = mongo.db[ConfigClass.USER_COLLECTION]
        existing_user = user_col.find_one({'email': email})

        if not existing_user:
            random_password = secrets.token_urlsafe(10)
            hashed_password = md5_hash(random_password)
            avatar = download_avatar(avatar_url, nama)

            new_user = {
                'name': nama,
                'email': email,
                'avatar': avatar,
                'role': 'user',
                'password': hashed_password
            }
            insert_result = user_col.insert_one(new_user)
            user_id = insert_result.inserted_id
        else:
            # Update avatar (opsional, bisa dihapus kalau tidak perlu update tiap login)
            avatar = download_avatar(avatar_url, existing_user['name'])
            user_col.update_one(
                {'_id': existing_user['_id']},
                {'$set': {'avatar': avatar}}
            )
            user_id = existing_user['_id']
            nama = existing_user['name']
            email = existing_user['email']
            avatar = avatar or existing_user.get('avatar')
            role = existing_user['role']

        access_token = create_access_token(
            identity=str(user_id),
            expires_delta=timedelta(days=1)
        )

        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'user': {
                    'id': str(user_id),
                    'name': nama,
                    'email': email,
                    'role': 'user',
                    'avatar': avatar
                },
                'token': access_token
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Terjadi kesalahan: {str(e)}'}), 500
