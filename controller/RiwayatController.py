from datetime import datetime
from config import ConfigClass
from controller.LogActivityController import simpan_log
from db import mongo
from flask import jsonify, request
from firebase.firebase_service import FirebaseService

notifikasi_collection = mongo.db[ConfigClass.NOTIFIKASI_COLLECTION]

def RequestRiwayat(current_user):
    # Mengambil seluruh riwayat latihan dari pengguna yang login
    client_api_key = request.headers.get('x-api-key')
    if not client_api_key or client_api_key != ConfigClass.API_KEY:
        return jsonify({
            "status": "Gagal",
            "message": "API key tidak valid"
        }), 401
    
    riwayat_data = mongo.db.riwayat.find({'user_id': current_user['_id']})  

    riwayat_list = []

    for riwayat in riwayat_data:
        gerakan_name = riwayat.get('gerakan_name', 'Tidak ada')
        riwayat_list.append({
            "id": str(riwayat['_id']),
            "date": riwayat['date'],
            "tari_name": riwayat['tari_name'],
            "gerakan_name": gerakan_name,
            "score": riwayat['score']  # Menampilkan skor gabungan
        })

    return jsonify({
        "status": "Berhasil",
        "message": "Data riwayat berhasil diambil",
        "data": riwayat_list
    }), 200


# --------------------------- Belum dipakai -------------
def add_riwayat(current_user):
    data = request.get_json()
    date = data.get('date')  
    tari_name = data.get('tari_name')
    gerakan_name = data.get('gerakan_name') 
    score = data.get('score')
    
    client_api_key = request.headers.get('x-api-key')
    if not client_api_key or client_api_key != ConfigClass.API_KEY:
        return jsonify({
            "status": "Gagal",
            "message": "API key tidak valid"
        }), 401
    
    if not date or not tari_name or not gerakan_name or score is None:
        return jsonify({'status': 'gagal', 'pesan': 'Semua field wajib diisi'}), 400

    # Menyimpan data riwayat ke MongoDB
    riwayat = {
        'user_id': current_user['_id'],  # ID pengguna yang sedang login
        'date': date,
        'tari_name': tari_name,
        'gerakan_name': gerakan_name,
        'score': score  # Menyimpan skor gabungan
    }
    current_time = datetime.utcnow()
    result = mongo.db.riwayat.insert_one(riwayat)
    simpan_log(str(current_user['_id']), current_user['email'], f"Menambahkan riwayat latihan {tari_name} dengan skor {score}")
    # Kirim notifikasi via Firebase
    FirebaseService.send_notification(
        title="Selamat anda sudah menyelesaikan latihan",
        body=f"Selamat anda sudah menyelesaikan latihan dengan {score} untuk {tari_name} {gerakan_name}",
        topic=f"notif_user_{str(current_user['_id'])}",
        data={
            "isRead": "false",
            "time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

        # Simpan notifikasi ke database
    notifikasi_collection.insert_one({
        'email': current_user['email'],
        'title': 'Selamat anda sudah menyelesaikan latihan',
        'body': f'Selamat anda sudah menyelesaikan latihan dengan {score} untuk {tari_name} {gerakan_name}',
        'topic': f"notif_user_{str(current_user['_id'])}",
        'isRead': False,
        'time': current_time
    })

    return jsonify({
        'status': 'sukses',
        'pesan': 'Riwayat latihan berhasil ditambahkan',
        'data': {
            'id': str(result.inserted_id),
            'date': date,
            'tari_name': tari_name,
            'gerakan_name': gerakan_name,
            'score': score
        }
    }), 201


def RequestByDate(current_user, date):
    # Mengambil riwayat latihan berdasarkan tanggal dan pengguna yang login
    riwayat_data = mongo.db.riwayat.find({'user_id': current_user['_id'], 'date': date})

    riwayat_list = []

    for riwayat in riwayat_data:
        riwayat_list.append({
            "id": str(riwayat['_id']),
            "date": riwayat['date'],
            "tari_name": riwayat['tari_name'],
            "score": riwayat['score']  # Menampilkan skor gabungan
        })

    return jsonify({
        "status": "Berhasil",
        "message": "Data riwayat berhasil diambil",
        "data": riwayat_list
    }), 200