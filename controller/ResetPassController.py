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

    # Mencari entri OTP di MongoDB
    reset_entry = mongo.db[ConfigClass.RESET_PASSWORD_COLLECTION].find_one({'token': otp})
    if not reset_entry:
        return jsonify({'message': 'OTP tidak valid!'}), 400

    # Verifikasi apakah OTP yang dimasukkan sesuai dan masih berlaku
    if reset_entry['expiry'] < datetime.utcnow():
        return jsonify({'message': 'OTP sudah kadaluarsa!'}), 400

    try:
        # Mencari pengguna berdasarkan user_id dari entri OTP
        user = mongo.db[ConfigClass.USER_COLLECTION].find_one({'_id': ObjectId(reset_entry['user_id'])})
        if not user:
            return jsonify({'message': 'Pengguna tidak ditemukan!'}), 404

        # Reset password pengguna dengan hash MD5
        new_password_hashed = hashlib.md5(new_password.encode('utf-8')).hexdigest()
        mongo.db[ConfigClass.USER_COLLECTION].update_one(
            {'_id': ObjectId(reset_entry['user_id'])},
            {'$set': {'password': new_password_hashed}}
        )

        # Hapus entri OTP setelah digunakan
        mongo.db[ConfigClass.RESET_PASSWORD_COLLECTION].delete_one({'token': otp})

        return jsonify({'message': 'Password berhasil direset!'}), 200

    except Exception as e:
        return jsonify({'message': 'Terjadi kesalahan saat mereset password!'}), 500