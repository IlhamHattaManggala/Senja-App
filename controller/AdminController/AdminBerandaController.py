from flask import redirect, render_template, session

def admin_beranda():
    if 'admin' not in session:
        return redirect('/login-admin.html')
    return render_template('beranda-admin.html')