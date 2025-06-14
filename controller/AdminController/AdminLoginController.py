from datetime import datetime, timedelta
from flask import jsonify, redirect, render_template, request, session
from db import mongo
from config import ConfigClass
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf.csrf import generate_csrf
from controller.LogActivityController import simpan_log

def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    ip = request.remote_addr or 'unknown_ip'
    now = datetime.utcnow()

    # Inisialisasi login attempts
    if 'login_attempts' not in session:
        session['login_attempts'] = {}

    attempts = session['login_attempts'].get(ip, {"count": 0, "last_attempt": now.isoformat()})
    last_attempt_time = datetime.fromisoformat(attempts["last_attempt"])
    count = attempts["count"]

    # Blokir jika terlalu banyak gagal login dalam 5 menit
    if count >= 3 and (now - last_attempt_time) < timedelta(minutes=5):
        return jsonify({"pesan": "Terlalu banyak gagal login. Coba lagi 5 menit."}), 403

    user = mongo.db[ConfigClass.USER_COLLECTION].find_one({'email': email})

    # Cek apakah user ada dan punya role admin
    if user and user.get('role') == 'admin' and check_password_hash(user['password'], password):
        session['admin'] = str(user['_id'])  # Login berhasil → simpan session
        session['login_attempts'][ip] = {"count": 0, "last_attempt": now.isoformat()}  # reset count
        simpan_log(str(user['_id']), user['email'], "Login sebagai admin")
        return jsonify({'pesan': 'Login berhasil!', 'data': {'token': 'session'}})
    else:
        # Gagal login → tambah counter
        session['login_attempts'][ip] = {
            "count": count + 1,
            "last_attempt": now.isoformat()
        }
        return jsonify({'pesan': 'Email, password, atau role salah!'}), 401

def admin_logout():
    if 'admin' in session:
        session.pop('admin', None)  # Hapus session admin
        return redirect('/login-admin.html')
    else:
        return jsonify({'pesan': 'Anda belum login!'}), 401

def admin_check_login():
    if 'admin' in session:
        return redirect('/beranda-admin.html')
    csrf_token = generate_csrf()
    return render_template('login-admin.html', csrf_token=csrf_token)
