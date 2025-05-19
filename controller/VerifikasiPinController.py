from flask import jsonify, request
from db import mongo
from itsdangerous import URLSafeTimedSerializer as Serializer
from config import ConfigClass
from datetime import datetime

def VerifyPin():
    try:
        data = request.json
        otp = data.get('otp')
        client_api_key = request.headers.get('x-api-key')

        # Validasi API key
        if not client_api_key or client_api_key != ConfigClass.API_KEY:
            return jsonify({
                "status": "Gagal",
                "message": "API key tidak valid"
            }), 401

        # Validasi input
        if not otp:
            return jsonify({'message': 'OTP harus diisi!'}), 400

        reset_pass_coll = mongo.db[ConfigClass.RESET_PASSWORD_COLLECTION]

        # Cari entry OTP yang sesuai dengan token
        reset_entry = reset_pass_coll.find_one({'token': otp})
        if not reset_entry:
            return jsonify({'message': 'OTP tidak valid!'}), 405

        # Verifikasi apakah OTP masih berlaku
        if reset_entry['expiry'] < datetime.utcnow():
            return jsonify({'message': 'OTP sudah kadaluarsa!'}), 403

        # Jika valid
        return jsonify({'success': True, 'message': 'OTP valid! Silakan lanjutkan dengan reset password.'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Terjadi kesalahan: {str(e)}'}), 500
