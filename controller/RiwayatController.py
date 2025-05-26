from datetime import date, datetime
from db import mongo
from flask import jsonify, request
from config import configClass
from firebase.firebase_service import FirebaseService

def RequestRiwayat(current_user):
    # Mengambil seluruh riwayat latihan dari pengguna yang login
    
    riwayat_data = mongo.db.riwayat.find({'user_id': current_user['_id']})  

    riwayat_list = []

    for riwayat in riwayat_data:
        riwayat_list.append({
            "id": str(riwayat['_id']),
            "date": riwayat['date'],
            "tari_name": riwayat['tari_name'],
            "gerakan_name": riwayat['gerakan_name'],
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
    notifikasi_collection = configClass.NOTIFIKASI_COLLECTION
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    FirebaseService.send_notification(
        title = "Selamat Anda telah menyelesaikan latihan",
        body= f"Selamat anda sudah menyelesaikan latihan {tari_name} {gerakan_name} dengan skor akhir {score}, semoga bermanfaat!",
        topic= "latihan_selesai",
        data={
            "isRead": "false",  # Mengirimkan status isRead
            "time": current_time,  # Mengirimkan waktu notifikasi
        }
    )
    user_data = mongo.db.users.find_one({'_id': current_user['_id']})
    email = user_data.get('email') if user_data else ''
    mongo.db[notifikasi_collection].insert_one({
        'email': email,
        'title': "Selamat Anda telah menyelesaikan latihan",
        'body': f"Selamat anda sudah menyelesaikan latihan {tari_name} {gerakan_name} dengan skor akhir {score}, semoga bermanfaat!",
        'topic': "latihan_selesai",
        'isRead': False,
        'time': current_time,
    })

    result = mongo.db.riwayat.insert_one(riwayat)

    return jsonify({
        'succes': 'sukses',
        'pesan': 'Riwayat latihan berhasil ditambahkan',
        'data': {
            'id': str(result.inserted_id),
            'date': date,
            'tari_name': tari_name,
            'gerakan_name': gerakan_name,
            'score': score
        }
    }), 200


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