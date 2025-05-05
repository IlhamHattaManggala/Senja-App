from flask import url_for, jsonify, request
from db import mongo
from config import ConfigClass, configClass

user_collection = mongo.db[ConfigClass.USER_COLLECTION]

def RequestProfile(current_user):
    print(current_user)  # Debugging untuk verifikasi current_user
    api_key = request.headers.get('x-api-key')
    
    if api_key not in configClass.API_KEY:
        return jsonify({'pesan': 'API key tidak valid'}), 403
    
    avatar_filename = current_user['avatar']
    avatar_url = url_for('static', filename=f'img/avatar/{avatar_filename}', _external=True)
    
    return jsonify({
        'status': 'sukses',
        'data': {
            'name': current_user['name'],
            'email': current_user['email'],
            'role': current_user['role'],
            'avatar': avatar_url
        }
    }), 200