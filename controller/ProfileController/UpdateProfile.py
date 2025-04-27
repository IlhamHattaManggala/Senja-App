from flask import request, jsonify
from db import mongo
from bson import ObjectId

def RequestUpdateProfile(current_user):
    update_data = request.get_json()

    # Data yang ingin diperbarui
    name = update_data.get('name')
    email = update_data.get('email')
    avatar = update_data.get('avatar')
    role = update_data.get('role')  # Ambil role baru jika ada, ganti dari 'user' menjadi 'role'

    # Validasi bahwa setidaknya satu data perlu diperbarui
    if not name and not email and not avatar and not role:
        return jsonify({'status': 'gagal', 'pesan': 'Minimal satu data harus diupdate'}), 400

    # Jika email diubah, cek apakah email sudah digunakan oleh pengguna lain
    if email and mongo.db.users.find_one({'email': email}):
        return jsonify({'status': 'gagal', 'pesan': 'Email sudah digunakan oleh pengguna lain'}), 409

    # Update data yang valid
    update_values = {}
    if name:
        update_values['name'] = name
    if email:
        update_values['email'] = email
    if avatar:
        update_values['avatar'] = avatar
    if role:
        update_values['role'] = role  # Pastikan role diupdate dengan benar

    # Memperbarui data pengguna di MongoDB
    mongo.db.users.update_one({'_id': ObjectId(current_user['_id'])}, {'$set': update_values})

    return jsonify({
        'status': 'sukses',
        'pesan': 'Profil berhasil diperbarui',
        'data': {
            'name': current_user['name'],
            'email': current_user['email'],
            'role': role if role else current_user['role'], 
            'avatar': current_user['avatar']
        }
    }), 200
