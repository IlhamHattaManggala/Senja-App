from flask import jsonify, request
from db import mongo
from itsdangerous import URLSafeTimedSerializer as Serializer
from config import ConfigClass
from datetime import datetime

def VerifyPin():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    # Cari entry OTP yang sesuai dengan email
    reset_entry = mongo.db[ConfigClass.RESET_PASSWORD_COLLECTION].find_one({'token': otp})
    if not reset_entry:
        return jsonify({'message': 'OTP tidak valid!'}), 400

    # Verifikasi apakah OTP yang dimasukkan sesuai dan masih berlaku
    if reset_entry['expiry'] < datetime.utcnow():
        return jsonify({'message': 'OTP sudah kadaluarsa!'}), 400

    if reset_entry.token == otp:
        return jsonify({'message': 'OTP valid! Silakan lanjutkan dengan reset password.'}), 200
    else:
        return jsonify({'message': 'OTP tidak valid!'}), 400