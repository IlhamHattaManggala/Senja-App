from flask import request, jsonify
from db import mongo
from config import ConfigClass
from datetime import datetime
import hashlib
from bson import ObjectId

def RequestResetPassword():
    data = request.json
    otp = data.get('otp')
    new_password = data.get('password')
    client_api_key = request.headers.get('x-api-key')

        # Validasi API key
    if not client_api_key or client_api_key != ConfigClass.API_KEY:
        return jsonify({
            "status": "Gagal",
            "message": "API key tidak valid"
        }), 401
    resetPass_collection = mongo.db[ConfigClass.RESET_PASSWORD_COLLECTION]
    user_collection = mongo.db[ConfigClass.USER_COLLECTION]

    # Mencari entri OTP di MongoDB
    reset_entry = resetPass_collection.find_one({'token': otp})
    if not reset_entry:
        return jsonify({'message': 'OTP tidak valid!'}), 400

    # Verifikasi apakah OTP yang dimasukkan sesuai dan masih berlaku
    if reset_entry['expiry'] < datetime.utcnow():
        return jsonify({'message': 'OTP sudah kadaluarsa!'}), 402

    try:
        # Mencari pengguna berdasarkan user_id dari entri OTP
        user = user_collection.find_one({'_id': ObjectId(reset_entry['user_id'])})
        if not user:
            return jsonify({'message': 'Pengguna tidak ditemukan!'}), 404

        # Reset password pengguna dengan hash MD5
        new_password_hashed = hashlib.md5(new_password.encode('utf-8')).hexdigest()
        user_collection.update_one(
            {'_id': ObjectId(reset_entry['user_id'])},
            {'$set': {'password': new_password_hashed}}
        )

        # Hapus entri OTP setelah digunakan
        resetPass_collection.delete_one({'token': otp})

        return jsonify({'success': True, 'message': 'Password berhasil direset!'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': 'Terjadi kesalahan saat mereset password!'}), 500