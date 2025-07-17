from bson import ObjectId
from flask import jsonify, request
from db import mongo
from config import ConfigClass
from datetime import datetime
from firebase.firebase_service import FirebaseService  # ✅ pastikan ini diimport

def RequestVerifyEmail(current_user):
    data = request.json
    otp = data.get('otp')
    client_api_key = request.headers.get('x-api-key')
    
    if not client_api_key or client_api_key != ConfigClass.API_KEY:
        return jsonify({
            "status": "Gagal",
            "message": "API key tidak valid"
        }), 401

    if not otp:
        return jsonify({'message': 'OTP harus diisi!'}), 400

    verify_collection = mongo.db[ConfigClass.VERIFY_EMAIL_COLLECTION]
    notifikasi_collection = mongo.db[ConfigClass.NOTIFIKASI_COLLECTION]  # ✅ pastikan ini
    user_id = current_user['_id']

    verify_entry = verify_collection.find_one({'user_id': user_id})
    if not verify_entry:
        return jsonify({
            "status": "Gagal",
            "message": "Data verifikasi tidak ditemukan"
        }), 404

    if verify_entry.get('emailVerifyAt') is not None:
        return jsonify({
            "status": "Gagal",
            "message": "Email sudah diverifikasi sebelumnya"
        }), 400

    if verify_entry.get('otp') != otp:
        return jsonify({
            "status": "Gagal",
            "message": "OTP salah"
        }), 400

    if verify_entry.get('expiry') < datetime.utcnow():
        return jsonify({
            "status": "Gagal",
            "message": "OTP sudah kadaluarsa"
        }), 400

    # ✅ Verifikasi sukses
    verified_time = datetime.utcnow()
    verify_collection.update_one(
        {'user_id': user_id},
        {'$set': {'emailVerifyAt': verified_time}}
    )

    # Ambil email user dari database
    user = mongo.db[ConfigClass.USER_COLLECTION].find_one({'_id': user_id})
    email = user.get('email', '')
    name = user.get('name', '')

    # 🔔 Kirim notifikasi via Firebase berdasarkan topik user
    FirebaseService.send_notification(
        title="Akun Anda telah terverifikasi",
        body=f"Halo {name}, akun Anda berhasil diverifikasi! Selamat datang!",
        topic=f"notif_user_{str(user_id)}",
        data={
            "isRead": "false",
            "time": verified_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

    # 🗂 Simpan notifikasi ke MongoDB
    notifikasi_collection.insert_one({
        'email': email,
        'title': "Akun Anda telah terverifikasi",
        'body': f"Halo {name}, akun Anda berhasil diverifikasi! Selamat datang!",
        'topic': f"notif_user_{str(user_id)}",
        'isRead': False,
        'time': verified_time
    })

    return jsonify({
        "status": "Berhasil",
        "message": "Akun berhasil diverifikasi",
        "verifiedAt": verified_time.strftime("%Y-%m-%d %H:%M:%S")
    }), 200
