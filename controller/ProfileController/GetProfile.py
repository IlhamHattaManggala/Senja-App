from flask import url_for, jsonify

def RequestProfile(current_user):
    print(current_user)  # Debugging untuk verifikasi current_user
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