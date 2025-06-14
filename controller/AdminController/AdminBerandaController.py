from bson import ObjectId
from db import mongo
from config import ConfigClass
from flask import session, render_template, redirect

def admin_beranda():
    if 'admin' not in session:
        return redirect('/login-admin.html')
    
    admin_id = session['admin']
    admin = mongo.db[ConfigClass.USER_COLLECTION].find_one({'_id': ObjectId(admin_id)})

    return render_template('beranda-admin.html', admin=admin)