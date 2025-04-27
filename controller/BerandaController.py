from flask import request, jsonify
from db import mongo

def RequestBeranda(current_user):
    base_url = request.host_url.rstrip('/') + '/static/img'

    # --- Tari Section ---
    tari_data = mongo.db.tari.find()
    tari_list = []

    for tari in tari_data:
        gerakan_list = []
        gerakan_data = mongo.db.gerakan.find({'tari_id': tari['_id']})

        for gerakan in gerakan_data:
            gerakan_list.append({
                "name": gerakan['name'],
                "imageUrl": f"{base_url}/gerakan/{gerakan['imageUrl']}" if 'imageUrl' in gerakan else None
            })

        image_url_tari = f"{base_url}/tari/{tari['imageUrl']}" if 'imageUrl' in tari else None

        tari_list.append({
            "name": tari['name'],
            "level": tari.get('level', 'Tidak diketahui'),
            "description": tari['description'],
            "imageUrl": image_url_tari,
            "asal": tari.get('asal', 'Tidak diketahui'),
            "gerakan": gerakan_list
        })

    # --- Seni Lainnya Section ---
    seni_lainnya_data = mongo.db.seni_lainnya.find()
    seni_lainnya_list = []

    for seni in seni_lainnya_data:
        image_url_seni = f"{base_url}/seni-lainnya/{seni['imageUrl']}" if 'imageUrl' in seni else None

        # 🔧 Proses detail agar imageUrl-nya lengkap
        detail_list = []
        for detail in seni.get('details', []):
            detail_list.append({
                "name": detail['name'],
                "description": detail['description'],
                "imageUrl": f"{base_url}/seni-lainnya/{detail['imageUrl']}" if 'imageUrl' in detail else None
            })

        seni_lainnya_list.append({
            "name": seni['name'],
            "description": seni['description'],
            "asal": seni['asal'],
            "category": seni['category'], 
            "imageUrl": image_url_seni,
            "details": detail_list
        })

    # Return Response
    return jsonify({
        "status": "Berhasil",
        "message": "Data berhasil diambil",
        "tari": tari_list,
        "seni_lainnya": seni_lainnya_list
    }), 200
