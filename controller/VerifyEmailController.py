from bson import ObjectId
from flask import jsonify, request
from db import mongo
from config import ConfigClass
from datetime import datetime

def RequestVerifyEmail(current_user):
    data = request.json
    otp = data.get('otp')
    client_api_key = request.headers.get('x-api-key')
    
    # Validasi API key
    if not client_api_key or client_api_key != ConfigClass.API_KEY:
        return jsonify({
            "status": "Gagal",
            "message": "API key tidak valid"
        }), 401
    
    # Validasi OTP
    if not otp:
        return jsonify({'message': 'OTP harus diisi!'}), 400
    
    verify_collection = mongo.db[ConfigClass.VERIFY_EMAIL_COLLECTION]
    user_id = current_user['_id']
    
    # Cari data verifikasi di verify_collection
    verify_entry = verify_collection.find_one({'user_id': user_id})
    
    if not verify_entry:
        return jsonify({
            "status": "Gagal",
            "message": "Data verifikasi tidak ditemukan"
        }), 404
    
    # Cek apakah email sudah diverifikasi
    if verify_entry.get('emailVerifyAt') is not None:
        return jsonify({
            "status": "Gagal",
            "message": "Email sudah diverifikasi sebelumnya"
        }), 400
    
    # Cek kecocokan OTP
    if verify_entry.get('otp') != otp:
        return jsonify({
            "status": "Gagal",
            "message": "OTP salah"
        }), 400
    
    # Cek expiry OTP
    if verify_entry.get('expiry') < datetime.utcnow():
        return jsonify({
            "status": "Gagal",
            "message": "OTP sudah kadaluarsa"
        }), 400
    
    # Update emailVerifyAt jika semua valid
    verified_time = datetime.utcnow()
    verify_collection.update_one(
        {'user_id': user_id},
        {'$set': {'emailVerifyAt': verified_time}}
    )
    
    return jsonify({
        "status": "Berhasil",
        "message": "Akun berhasil diverifikasi",
        "verifiedAt": verified_time.strftime("%Y-%m-%d %H:%M:%S")
    }), 200
