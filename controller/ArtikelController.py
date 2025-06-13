from flask import jsonify, request
from flask_pymongo import DESCENDING
from db import mongo
from config import ConfigClass
import math

def RequestArtikel(current_user):
    client_api_key = request.headers.get('x-api-key')
    if not client_api_key or client_api_key != ConfigClass.API_KEY:
        return jsonify({
            "status": "Gagal",
            "message": "API key tidak valid"
        }), 401

    page = int(request.args.get('page', 1))
    per_page = 10
    skip_count = (page - 1) * per_page

    # Hitung total dokumen
    total_items = mongo.db[ConfigClass.TARI_ARTICLE_COLLECTION].count_documents({})
    total_pages = math.ceil(total_items / per_page)

    # Ambil data artikel
    tari_list = list(
        mongo.db[ConfigClass.TARI_ARTICLE_COLLECTION]
        .find()
        .sort("date", DESCENDING)
        .skip(skip_count)
        .limit(per_page)
    )

    for item in tari_list:
        item['id'] = str(item['_id'])
        
    return jsonify({
        "status": "Berhasil",
        "data": tari_list,
        "total_pages": total_pages,
        "current_page": page
    })
