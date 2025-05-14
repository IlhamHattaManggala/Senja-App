from flask import request, jsonify
from db import mongo
from werkzeug.security import generate_password_hash
from datetime import datetime
from firebase.firebase_service import FirebaseService
from config import configClass
def RequestRegister():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    api_key = request.headers.get('x-api-key')
    
    if api_key not in configClass.API_KEY:
        return jsonify({'pesan': 'API key tidak valid'}), 403
    
    user_collection = configClass.USER_COLLECTION
    notifikasi_collection = configClass.NOTIFIKASI_COLLECTION

    if not name or not email or not password:
        return jsonify({'pesan': 'Semua field wajib diisi'}), 400

    if mongo.db.users.find_one({'email': email}):
        return jsonify({'pesan': 'Email sudah digunakan'}), 409

    hashed_password = generate_password_hash(password)
    avatar = "default-icon.png"

    user = {
        'name': name,
        'email': email,
        'password': hashed_password,
        'role': 'user', 
        'avatar': avatar
    }
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = mongo.db[user_collection].insert_one(user)
    user['_id'] = result.inserted_id
    FirebaseService.send_notification(
        title = "Terima kasih telah mendaftar",
        body="Selamat datang di aplikasi kami!, kami senang Anda bergabung. Selamat menggunakan aplikasi kami!",
        topic="user_baru",
        data={
            "isRead": "false",  # Mengirimkan status isRead
            "time": current_time,  # Mengirimkan waktu notifikasi
        }
    )

    mongo.db[notifikasi_collection].insert_one({
        'email': email,
        'title': 'Terima kasih telah mendaftar',
        'body': 'Selamat datang di aplikasi kami!, kami senang Anda bergabung. Selamat menggunakan aplikasi kami!',
        'topic': "user_baru",
        'isRead': False,
        'time': current_time,
    })

    return jsonify({
        'status': 'sukses',
        'pesan': 'Registrasi berhasil',
        'data': {
            'user': {
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email']
            }
        }
    }), 201