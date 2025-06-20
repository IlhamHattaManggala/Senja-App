from datetime import datetime, timedelta
import hashlib
import random
import secrets
import os
from flask_mail import Mail
import requests
from flask import jsonify, request
from firebase_admin import auth
from flask_jwt_extended import create_access_token
from werkzeug.utils import secure_filename
from config import ConfigClass
from db import mongo
from firebase.firebase_service import FirebaseService
from mail.sendVerifyAkun import send_verify_email
from controller.LogActivityController import simpan_log  

mail = Mail()

otp_expiry_time = 300
verifikasi_collection = mongo.db[ConfigClass.VERIFY_EMAIL_COLLECTION]
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
            return filename
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

        user_col = mongo.db[ConfigClass.USER_COLLECTION]
        existing_user = user_col.find_one({'email': email})

        if not existing_user:
            return jsonify({
                "status": "Gagal",
                "message": "Akun tidak ditemukan. Silakan hubungi admin atau daftar melalui metode lain."
            }), 404

        # Ambil data user yang sudah ada tanpa memperbarui apapun
        user_id = existing_user['_id']
        nama = existing_user['name']
        avatar = existing_user.get('avatar')
        role = existing_user['role']

        access_token = create_access_token(
            identity=str(user_id),
            expires_delta=timedelta(days=1)
        )
        
        simpan_log(str(user_id), email, "Login dengan Google dari aplikasi mobile")

        return jsonify({
            'status': 'success',
            'message': 'Login berhasil',
            'data': {
                'user': {
                    'id': str(user_id),
                    'name': nama,
                    'email': email,
                    'role': role,
                    'avatar': avatar
                },
                'token': access_token
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Terjadi kesalahan: {str(e)}'}), 500


def registerGoogle():
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

        if existing_user:
            return jsonify({
                "status": "Gagal",
                "message": "Email sudah terdaftar, silakan login."
            }), 409

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
        otp = str(random.randint(100000, 999999))
        otp_expiry = datetime.utcnow() + timedelta(seconds=otp_expiry_time)

        # Cek jika sudah ada data verify sebelumnya, update jika ada
        existing_entry = verifikasi_collection.find_one({'user_id': user_id})
        if existing_entry:
            verifikasi_collection.update_one(
                {'user_id': str(user_id)},
                {'$set': {
                    'otp': otp,
                    'expiry': otp_expiry,
                    'emailVerifyAt': None
                }}
            )
        else:
            otp_entry = {
                'user_id': user_id,
                'otp': otp,
                'expiry': otp_expiry,
                'emailVerifyAt': None
            }
            verifikasi_collection.insert_one(otp_entry)

        # Kirim email OTP
        send_verify_email(email, otp)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Kirim notifikasi ke topik "user_baru"
        FirebaseService.send_notification(
            title="Terima kasih telah mendaftar",
            body="Selamat datang di aplikasi kami!, kami senang Anda bergabung. Selamat menggunakan aplikasi kami!",
            topic="user_baru",
            data={
                "isRead": "false",
                "time": current_time
            }
        )

        mongo.db[ConfigClass.NOTIFIKASI_COLLECTION].insert_one({
            'email': email,
            'title': 'Terima kasih telah mendaftar',
            'body': 'Selamat datang di aplikasi kami!, kami senang Anda bergabung. Selamat menggunakan aplikasi kami!',
            'topic': "user_baru",
            'isRead': False,
            'time': current_time,
        })

        access_token = create_access_token(
            identity=str(user_id),
            expires_delta=timedelta(days=1)
        )
        simpan_log(str(user_id), email, "Registrasi dengan Google dari aplikasi mobile")
        
        return jsonify({
            'status': 'success',
            'message': 'Registrasi berhasil',
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
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f'Terjadi kesalahan: {str(e)}'}), 500
