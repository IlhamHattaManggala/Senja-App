from bson import ObjectId
from flask import redirect, request, session, render_template, url_for
from db import mongo
from config import ConfigClass
from werkzeug.security import generate_password_hash


def datas():
    if 'admin' not in session:
        return redirect('/login-admin.html')
    users = list(mongo.db[ConfigClass.USER_COLLECTION].find({}, {"password": 0}))
    return render_template('data-pengguna.html', users=users)

def tari_data():
    if 'admin' not in session:
        return redirect('/login-admin.html')
    tari_list = list(mongo.db[ConfigClass.TARI_COLLECTION].find())
    return render_template('data-tari.html', tari_list=tari_list)

def informasi_lainnya():
    if 'admin' not in session:
        return redirect('/login-admin.html')
    data = list(mongo.db[ConfigClass.SENI_LAINNYA_COLLECTION].find())
    return render_template('data-informasi-lainnya.html', data=data)

def edit_informasi(item_id):
    item = mongo.db[ConfigClass.SENI_LAINNYA_COLLECTION].find_one({'_id': ObjectId(item_id)})
    return render_template('edit-informasi-lainnya.html', item=item)

def update_informasi(item_id):
    name = request.form['name']
    category = request.form['category']
    asal = request.form['asal']
    description = request.form['description']
    imageUrl = request.form['imageUrl']
    mongo.db['seni_lainnya'].update_one(
        {'_id': ObjectId(item_id)},
        {'$set': {
            'name': name,
            'category': category,
            'asal': asal,
            'description': description,
            'imageUrl': imageUrl
        }}
    )
    return redirect(url_for('data_informasi_lainnya'))

def delete_informasi(item_id):
    mongo.db[ConfigClass.SENI_LAINNYA_COLLECTION].delete_one({'_id': ObjectId(item_id)})
    return redirect(url_for('data_informasi_lainnya'))

def tari_edit(tari_id):
    tari = mongo.db[ConfigClass.TARI_COLLECTION].find_one({'_id': ObjectId(tari_id)})
    return render_template('edit-tari.html', tari=tari)

def update_taris(tari_id):
    name = request.form['name']
    level = request.form['level']
    asal = request.form['asal']
    description = request.form['description']
    mongo.db[ConfigClass.TARI_COLLECTION].update_one(
        {'_id': ObjectId(tari_id)},
        {'$set': {
            'name': name,
            'level': level,
            'asal': asal,
            'description': description
        }}
    )
    return redirect(url_for('data_tari'))

def delete_taris(tari_id):
    mongo.db[ConfigClass.TARI_COLLECTION].delete_one({'_id': ObjectId(tari_id)})
    return redirect(url_for('data_tari'))

def user_edit(user_id):
    user = mongo.db[ConfigClass.USER_COLLECTION].find_one({'_id': ObjectId(user_id)})
    return render_template('edit-user.html', user=user)

def user_update(user_id):
    name = request.form['name']
    email = request.form['email']
    mongo.db[ConfigClass.USER_COLLECTION].update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'name': name, 'email': email}}
    )
    return redirect(url_for('data_pengguna'))

def user_delete(user_id):
    mongo.db[ConfigClass.USER_COLLECTION].delete_one({'_id': ObjectId(user_id)})
    return redirect(url_for('data_pengguna'))

def add_pengguna():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        avatar = request.form['avatar']

        user_data = {
            'name': name,
            'email': email,
            'password': password,
            'role': role,
            'avatar': avatar if avatar else 'default-icon.png'
        }
        mongo.db[ConfigClass.USER_COLLECTION].insert_one(user_data)
        return redirect(url_for('data_pengguna'))
    return render_template('add-pengguna.html')

def add_tari():
    if request.method == 'POST':
        name = request.form['name']
        asal = request.form['asal']
        level = request.form['level']
        imageUrl = request.form.get('imageUrl', '')
        description = request.form['description']
        
        detail_name = request.form.get('detail_name')
        detail_image = request.form.get('detail_image')
        detail_video = request.form.get('detail_video')

        gerakan = []
        if detail_name and detail_image and detail_video:
            gerakan.append({
                'name': detail_name,
                'imageUrl': detail_image,
                'videoUrl': detail_video,
                'skor': ''
            })

        mongo.db[ConfigClass.TARI_COLLECTION].insert_one({
            'name': name,
            'asal': asal,
            'level': level,
            'imageUrl': imageUrl,
            'description': description,
            'gerakan': gerakan
        })
        return redirect(url_for('data_tari'))
    return render_template('add-tari.html')

def add_informasi_lainnya():
    if request.method == 'POST':
        name = request.form['name']
        asal = request.form['asal']
        category = request.form['category']
        imageUrl = request.form['imageUrl']
        description = request.form['description']
        
        detail_name = request.form.get('detail_name')
        detail_image = request.form.get('detail_image')
        detail_description = request.form.get('detail_description')

        details = []
        if detail_name and detail_image and detail_description:
            details.append({
                'name': detail_name,
                'imageUrl': detail_image,
                'description': detail_description
            })

        mongo.db[ConfigClass.SENI_LAINNYA_COLLECTION].insert_one({
            'name': name,
            'asal': asal,
            'category': category,
            'imageUrl': imageUrl,
            'description': description,
            'details': details
        })
        return redirect(url_for('data_informasi_lainnya'))
    return render_template('add-informasi-lainnya.html')