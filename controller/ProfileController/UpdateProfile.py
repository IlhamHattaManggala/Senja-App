from flask import request, jsonify
from db import mongo
from bson import ObjectId
from config import ConfigClass, allowed_file, secure_filename
import os
from werkzeug.security import generate_password_hash

user_collection = mongo.db[ConfigClass.USER_COLLECTION]

def RequestUpdateProfile(current_user):
    data = request.form
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    avatar = request.files.get('avatar')

    update_data = {}
    if name:
        update_data['name'] = name

    if email:
        existing = user_collection.find_one({'email': email})
        if existing and str(existing['_id']) != str(current_user['_id']):
            return jsonify({'status': 'gagal', 'pesan': 'Email sudah digunakan'}), 409
        update_data['email'] = email

    if password:
        update_data['password'] = generate_password_hash(password)

    if avatar and allowed_file(avatar.filename):
        username = current_user['name'] if 'name' in current_user else "user"
        filename = secure_filename(username.lower().replace(" ", "_")) + ".jpg"
        folder_path = os.path.join("static", "img", "avatar")
        os.makedirs(folder_path, exist_ok=True)
        filepath = os.path.join(folder_path, filename)

        avatar.save(filepath)

        avatar_url = filename
        update_data['avatar'] = avatar_url

    user_collection.update_one(
        {'_id': ObjectId(current_user['_id'])},
        {'$set': update_data}
    )

    updated_user = user_collection.find_one({'_id': ObjectId(current_user['_id'])})
    updated_user['_id'] = str(updated_user['_id'])
    updated_user.pop('password', None)

    return jsonify({'status': 'sukses', 'data': updated_user}), 200
