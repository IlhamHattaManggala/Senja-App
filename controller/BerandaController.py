from flask import request, jsonify
from db import mongo
from config import ConfigClass

tari_collection = mongo.db[ConfigClass.TARI_COLLECTION]
seniLainnya_collection = mongo.db[ConfigClass.SENI_LAINNYA_COLLECTION]

def RequestBeranda(current_user):
    client_api_key = request.headers.get('x-api-key')
    if not client_api_key or client_api_key != ConfigClass.API_KEY:
        return jsonify({
            "status": "Gagal",
            "message": "API key tidak valid"
        }), 401
    base_url = request.host_url.rstrip('/') + '/static/img'
    base = request.host_url.rstrip('/')

    # --- Tari Section ---
    tari_data = tari_collection.find()
    tari_list = []

    for tari in tari_data:
        gerakan_list = []
        
        for gerakan in tari.get('gerakan',[]):
            image_url = f"{base_url}/gerakan/{gerakan['imageUrl']}" if 'imageUrl' in gerakan else None
            video_url = f"{base}/static/vidio/{gerakan['videoUrl']}" if 'videoUrl' in gerakan else None
            gerakan_list.append({
                "name": gerakan['name'],
                "imageUrl": image_url,
                "videoUrl": video_url,
                "previewVideo": gerakan['videoUrl']
            })

        image_url_tari = f"{base_url}/tari/{tari['imageUrl']}" if 'imageUrl' in tari else None

        tari_list.append({
            "name": tari['name'],
            "level": tari.get('level', 'Tidak diketahui'),
            "description": tari['description'],
            "imageUrl": image_url_tari,
            "asal": tari.get('asal', 'Tidak diketahui'),
            "gerakanTari": gerakan_list
        })

    # --- Seni Lainnya Section ---
    seni_lainnya_data = seniLainnya_collection.find()
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
