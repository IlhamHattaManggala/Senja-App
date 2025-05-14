import datetime
from bson import ObjectId
from flask_jwt_extended import get_jwt_identity
from flask import jsonify, request
from config import ConfigClass
from db import mongo

notifikasi_collection = mongo.db[ConfigClass.NOTIFIKASI_COLLECTION]
user_collection = mongo.db[ConfigClass.USER_COLLECTION]

def buatNotifikasi():
    try:
        # Mengambil data dari body request
        data = request.get_json()
        title = data.get('title')
        body = data.get('body')

        # Validasi input
        if not title or not body:
            return jsonify({"message": "Judul dan body wajib diisi"}), 400

        # Mendapatkan user_id dari JWT
        user_id = get_jwt_identity()

        # Mencari pengguna di database
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"message": "Pengguna tidak ditemukan"}), 404

        # Membuat notifikasi
        notification = {
            "title": title,
            "body": body,
            "isRead": False,  # Menandakan bahwa notifikasi belum dibaca
            "user_id": ObjectId(user_id),  # Menyimpan ID pengguna yang terkait
            "created_at": datetime.datetime.now()
        }

        # Menyimpan notifikasi ke dalam database
        notifikasi_collection.insert_one(notification)

        return jsonify({"message": "Notifikasi berhasil dibuat"}), 201

    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500


def getAllNotifikasi():
    try:
        client_api_key = request.headers.get('x-api-key')
        if not client_api_key or client_api_key != ConfigClass.API_KEY:
            return jsonify({
                "status": "Gagal",
                "message": "API key tidak valid"
            }), 401
        user_id = get_jwt_identity()  # Ambil ID dari JWT
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"status": "error", "message": "User tidak ditemukan"}), 404

        email = user.get("email")
        if not email:
            return jsonify({"status": "error", "message": "Email tidak ditemukan"}), 400

        notifikasi_cursor = notifikasi_collection.find({"email": email})
        notifikasi_data = []
        for notif in notifikasi_cursor:
            notif['_id'] = str(notif['_id'])
            notifikasi_data.append(notif)

        return jsonify({
            "status": "success",
            "message": "Data notifikasi berhasil diambil",
            "notifikasi": notifikasi_data
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Gagal mengambil data notifikasi: {str(e)}"}), 500

def readNotifikasi(notif_id):
    client_api_key = request.headers.get('x-api-key')
    if not client_api_key or client_api_key != ConfigClass.API_KEY:
        return jsonify({
            "status": "Gagal",
            "message": "API key tidak valid"
        }), 401
    result = notifikasi_collection.update_one(
        {'_id': ObjectId(notif_id)},
        {'$set': {'isRead': True}}
    )
    if result.matched_count == 0:
        return jsonify({'message': 'Notifikasi tidak ditemukan'}), 404
    return jsonify({'message': 'Notifikasi ditandai sebagai dibaca'}), 200

def deleteNotifikasi(notif_id):
    client_api_key = request.headers.get('x-api-key')
    if not client_api_key or client_api_key != ConfigClass.API_KEY:
        return jsonify({
            "status": "Gagal",
            "message": "API key tidak valid"
        }), 401
    result = notifikasi_collection.delete_one({'_id': ObjectId(notif_id)})
    if result.deleted_count == 0:
        return jsonify({'message': 'Notifikasi tidak ditemukan'}), 404
    return jsonify({'message': 'Notifikasi berhasil dihapus'}), 200

def kirim_notifikasi_hari_tari():
    try:
        # Data notifikasi
        title = "Selamat Hari Tari Sedunia!"
        body = "Hari ini adalah Hari Tari Sedunia. Mari kita rayakan bersama!"
        
        # Mengambil semua pengguna yang terdaftar
        users = user_collection.find()
        
        # Loop untuk mengirimkan notifikasi ke setiap pengguna
        for user in users:
            user_id = str(user["_id"])  # Ambil ID pengguna
            notification = {
                "title": title,
                "body": body,
                "isRead": False,  # Menandakan bahwa notifikasi belum dibaca
                "user_id": ObjectId(user_id),
                "created_at": datetime.datetime.now()
            }

            # Menyimpan notifikasi ke dalam database
            notifikasi_collection.insert_one(notification)

        print("Notifikasi Hari Tari Sedunia berhasil dikirim ke semua pengguna")

    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")