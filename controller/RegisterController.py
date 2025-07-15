import random
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from flask_mail import Mail
from db import mongo
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from firebase.firebase_service import FirebaseService
from config import ConfigClass, configClass
from mail.sendVerifyAkun import send_verify_email

mail = Mail()

otp_expiry_time = 300  # dalam detik, misal 5 menit
verify_collection = mongo.db[ConfigClass.VERIFY_EMAIL_COLLECTION]
user_collection = mongo.db[ConfigClass.USER_COLLECTION]
notifikasi_collection = mongo.db[ConfigClass.NOTIFIKASI_COLLECTION]

def RequestRegister():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'pesan': 'Data tidak ditemukan di request body'}), 400

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        api_key = request.headers.get('x-api-key')
        if not api_key or api_key != ConfigClass.API_KEY:
            return jsonify({'pesan': 'API key tidak valid'}), 401

        if not name or not email or not password:
            return jsonify({'pesan': 'Semua field wajib diisi'}), 403

        if user_collection.find_one({'email': email}):
            return jsonify({'pesan': 'Email sudah digunakan'}), 409

        hashed_password = generate_password_hash(password)
        avatar = "default-icon.png"
        current_time = datetime.utcnow()

        user = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'role': 'user',
            'avatar': avatar,
            'createdAt': current_time
        }

        result = user_collection.insert_one(user)
        user_id = str(result.inserted_id)  # KONVERSI KE STRING

        create_verifikasi_entry(user_id, email, verify_collection)

        FirebaseService.send_notification(
            title="Terima kasih telah mendaftar",
            body="Selamat datang di aplikasi kami!, kami senang Anda bergabung.",
            topic="user_baru",
            data={
                "isRead": "false",
                "time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        notifikasi_collection.insert_one({
            'email': email,
            'title': 'Terima kasih telah mendaftar',
            'body': 'Selamat datang di aplikasi kami!, kami senang Anda bergabung.',
            'topic': "user_baru",
            'isRead': False,
            'time': current_time
        })

        access_token = create_access_token(identity=user_id, expires_delta=timedelta(days=1))

        return jsonify({
            'status': 'sukses',
            'pesan': 'Registrasi berhasil, silakan cek email anda untuk verifikasi!',
            'data': {
                'user': {
                    'id': user_id,
                    'name': name,
                    'email': email,
                    'role': 'user',
                    'avatar': avatar,
                },
                'token': access_token
            }
        }), 201

    except Exception as e:
        return jsonify({'pesan': 'Terjadi kesalahan pada server', 'error': str(e)}), 500


def RequestRegisterWithStaticOTP():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'pesan': 'Data tidak ditemukan di request body'}), 400

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        api_key = request.headers.get('x-api-key')
        if not api_key or api_key != ConfigClass.API_KEY:
            return jsonify({'pesan': 'API key tidak valid'}), 401

        if not name or not email or not password:
            return jsonify({'pesan': 'Semua field wajib diisi'}), 403

        if user_collection.find_one({'email': email}):
            return jsonify({'pesan': 'Email sudah digunakan'}), 409

        hashed_password = generate_password_hash(password)
        avatar = "default-icon.png"
        current_time = datetime.utcnow()

        user = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'role': 'user',
            'avatar': avatar,
            'createdAt': current_time
        }

        result = user_collection.insert_one(user)
        user_id = str(result.inserted_id)

        # Gunakan OTP tetap
        otp = "311202"
        otp_expiry = datetime.utcnow() + timedelta(seconds=otp_expiry_time)

        existing_entry = verify_collection.find_one({'user_id': user_id})
        if existing_entry:
            verify_collection.update_one(
                {'user_id': user_id},
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
            verify_collection.insert_one(otp_entry)

        send_verify_email(email, otp)

        FirebaseService.send_notification(
            title="Terima kasih telah mendaftar",
            body="Selamat datang di aplikasi kami!, kami senang Anda bergabung. Selamat menggunakan aplikasi kami!",
            topic="user_baru",
            data={
                "isRead": "false",
                "time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        notifikasi_collection.insert_one({
            'email': email,
            'title': 'Terima kasih telah mendaftar',
            'body': 'Selamat datang di aplikasi kami!, kami senang Anda bergabung. Selamat menggunakan aplikasi kami!',
            'topic': "user_baru",
            'isRead': False,
            'time': current_time
        })

        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(days=1)
        )

        return jsonify({
            'status': 'sukses',
            'pesan': 'Registrasi berhasil, silakan cek email anda untuk verifikasi!',
            'data': {
                'user': {
                    'id': user_id,
                    'name': name,
                    'email': email,
                    'role': 'user',
                    'avatar': avatar,
                },
                'token': access_token
            }
        }), 201

    except Exception as e:
        return jsonify({'pesan': 'Terjadi kesalahan pada server', 'error': str(e)}), 500

def create_verifikasi_entry(user_id: str, email: str, collection):
    otp = str(random.randint(100000, 999999))
    otp_expiry = datetime.utcnow() + timedelta(seconds=otp_expiry_time)

    existing_entry = collection.find_one({'user_id': user_id})
    if existing_entry:
        collection.update_one(
            {'user_id': user_id},
            {'$set': {
                'otp': otp,
                'expiry': otp_expiry,
                'emailVerifyAt': None
            }}
        )
    else:
        collection.insert_one({
            'user_id': user_id,
            'otp': otp,
            'expiry': otp_expiry,
            'emailVerifyAt': None
        })

    send_verify_email(email, otp)
