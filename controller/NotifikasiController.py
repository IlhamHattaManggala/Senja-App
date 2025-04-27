import datetime
from bson import ObjectId
from flask_jwt_extended import get_jwt_identity
from flask import jsonify, request
from db import mongo

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
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
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
        mongo.db.notifikasi.insert_one(notification)

        return jsonify({"message": "Notifikasi berhasil dibuat"}), 201

    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500


def getAllNotifikasi():
    try:
        user_id = get_jwt_identity()  # Ambil ID dari JWT
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"status": "error", "message": "User tidak ditemukan"}), 404

        email = user.get("email")
        if not email:
            return jsonify({"status": "error", "message": "Email tidak ditemukan"}), 400

        notifikasi_cursor = mongo.db.notifikasi.find({"email": email})
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
    result = mongo.db.notifikasi.update_one(
        {'_id': ObjectId(notif_id)},
        {'$set': {'isRead': True}}
    )
    if result.matched_count == 0:
        return jsonify({'message': 'Notifikasi tidak ditemukan'}), 404
    return jsonify({'message': 'Notifikasi ditandai sebagai dibaca'}), 200

def deleteNotifikasi(notif_id):
    result = mongo.db.notifikasi.delete_one({'_id': ObjectId(notif_id)})
    if result.deleted_count == 0:
        return jsonify({'message': 'Notifikasi tidak ditemukan'}), 404
    return jsonify({'message': 'Notifikasi berhasil dihapus'}), 200
