from datetime import datetime, timedelta
from flask import jsonify, request
from db import mongo
from itsdangerous import URLSafeTimedSerializer as Serializer
from config import ConfigClass
from mail.SendMail import send_otp_email
from flask_mail import Mail
import random

# Inisialisasi Flask-Mail
mail = Mail()

otp_expiry_time = 300
resetPass_collection = mongo.db[ConfigClass.RESET_PASSWORD_COLLECTION]
user_collection = mongo.db[ConfigClass.USER_COLLECTION]

def RequestForgotPassword():
    email = request.json.get('email')

    # Cek apakah pengguna dengan email ini ada di MongoDB
    # user = mongo.db.users.find_one({'email': email})
    user = user_collection.find_one({'email': email})
    if not user:
        return jsonify({'message': 'Email tidak ditemukan!'}), 404

    # Generate OTP secara acak
    otp = str(random.randint(100000, 999999))
    otp_expiry = datetime.utcnow() + timedelta(seconds=otp_expiry_time)

    # Cek apakah sudah ada entri OTP di koleksi RESET_PASSWORD_COLLECTION untuk pengguna ini
    existing_entry = resetPass_collection.find_one({'user_id': str(user['_id'])})
    
    if existing_entry:
        # Update token dan expiry pada entri yang sudah ada
        resetPass_collection.update_one(
            {'user_id': str(user['_id'])},
            {'$set': {'token': otp, 'expiry': otp_expiry}}
        )
    else:
        # Buat entri baru jika belum ada
        otp_entry = {
            'user_id': str(user['_id']),
            'token': otp,
            'expiry': otp_expiry
        }
        resetPass_collection.insert_one(otp_entry)

    # Kirim OTP ke email pengguna
    send_otp_email(email, otp)
    
    return jsonify({'message': 'OTP reset password telah dikirim!'}), 200
