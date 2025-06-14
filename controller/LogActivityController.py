from flask import jsonify
from datetime import datetime
from db import mongo
from config import ConfigClass

# Ambil koleksi log_activity dari database
log_collection = mongo.db[ConfigClass.LOG_ACTIVITY_COLLECTION]

# ==================== FUNGSI SIMPAN LOG ====================
def simpan_log(user_id, email, aktivitas):
    try:
        print(f"[LOG] Menyimpan aktivitas: {aktivitas} oleh {email}")
        result = log_collection.insert_one({
            "user_id": user_id,
            "email": email,
            "aktivitas": aktivitas,
            "waktu": datetime.now()  # simpan sebagai datetime object
        })
        print(f"[LOG] Disimpan dengan ID: {result.inserted_id}")
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan log aktivitas: {e}")

# ==================== FUNGSI GET LOG PER USER ====================
def get_log_by_user(current_user):
    user_id = str(current_user['_id'])

    try:
        logs = log_collection.find({'user_id': user_id}).sort('waktu', -1)

        result = []
        for log in logs:
            raw_waktu = log.get('waktu')

            # Penanganan waktu dalam berbagai bentuk
            waktu_str = ""
            if isinstance(raw_waktu, datetime):
                waktu_str = raw_waktu.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(raw_waktu, str):
                try:
                    waktu_obj = datetime.fromisoformat(raw_waktu)
                    waktu_str = waktu_obj.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    waktu_str = raw_waktu  # fallback: string mentah
            else:
                waktu_str = "-"  # jika None atau tipe tidak dikenali

            result.append({
                'aktivitas': log.get('aktivitas', ''),
                'waktu': waktu_str
            })

        return jsonify({
            'status': 'sukses',
            'data': result
        }), 200

    except Exception as e:
        print(f"[ERROR get_log_by_user] {e}")
        return jsonify({'status': 'gagal', 'pesan': str(e)}), 500