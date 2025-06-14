from flask import request, jsonify
from db import mongo
from bson import ObjectId
from config import ConfigClass, allowed_file, secure_filename
import os
from werkzeug.security import generate_password_hash
from controller.LogActivityController import simpan_log

user_collection = mongo.db[ConfigClass.USER_COLLECTION]

def RequestUpdateProfile(current_user):
    data = request.form
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    avatar = request.files.get('avatar')
    client_api_key = request.headers.get('x-api-key')
    if not client_api_key or client_api_key != ConfigClass.API_KEY:
        return jsonify({
            "status": "Gagal",
            "message": "API key tidak valid"
        }), 401

    update_data = {}
    aktivitas_list = []

    # Cek apakah nama berubah
    if name and name != current_user.get('name'):
        update_data['name'] = name
        aktivitas_list.append("mengubah nama")

    # Cek apakah email berubah
    if email and email != current_user.get('email'):
        existing = user_collection.find_one({'email': email})
        if existing and str(existing['_id']) != str(current_user['_id']):
            return jsonify({'status': 'gagal', 'pesan': 'Email sudah digunakan'}), 409
        update_data['email'] = email
        aktivitas_list.append("mengubah email")

    # Cek apakah password diisi (tidak bisa dibandingkan karena di-hash)
    if password:
        update_data['password'] = generate_password_hash(password)
        aktivitas_list.append("mengubah password")

    # Cek apakah ada file avatar yang dikirim
    if avatar and allowed_file(avatar.filename):
        username = current_user.get('name', 'user')
        filename = secure_filename(username.lower().replace(" ", "_")) + ".jpg"
        folder_path = os.path.join("static", "img", "avatar")
        os.makedirs(folder_path, exist_ok=True)
        filepath = os.path.join(folder_path, filename)
        avatar.save(filepath)
        avatar_url = filename
        update_data['avatar'] = avatar_url
        aktivitas_list.append("mengubah avatar")

    # Lakukan update jika ada data yang diubah
    if update_data:
        user_collection.update_one(
            {'_id': ObjectId(current_user['_id'])},
            {'$set': update_data}
        )

        for aktivitas in aktivitas_list:
            simpan_log(
        str(current_user['_id']),
        current_user.get('email'),
        f"User melakukan {aktivitas} pada profil"
    )


    # Ambil data user terbaru untuk dikirim balik
    updated_user = user_collection.find_one({'_id': ObjectId(current_user['_id'])})
    updated_user['_id'] = str(updated_user['_id'])
    updated_user.pop('password', None)

    return jsonify({'status': 'sukses', 'data': updated_user}), 200
