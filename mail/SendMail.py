import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import ConfigClass

def send_otp_email(email, otp):
    sender_email = ConfigClass.MAIL_DEFAULT_SENDER  # Ganti dengan email pengirim
    sender_login_email = ConfigClass.MAIL_USERNAME
    sender_password = "lqkv ljza mhbi qpbx"  # Ganti dengan App Password Gmail
    recipient_email = email

    # Konten email dengan format HTML
    subject = "Kode OTP Reset Password Anda"
    body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                width: 100%;
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #4CAF50;
                text-align: center;
            }}
            p {{
                font-size: 16px;
                line-height: 1.6;
                text-align: center;
            }}
            .otp {{
                font-size: 20px;
                font-weight: bold;
                color: #007BFF;
                display: block;
                text-align: center;
                margin-top: 20px;
                padding: 10px;
                background-color: #e7f3fe;
                border: 1px solid #b3d6f7;
                border-radius: 5px;
            }}
            .footer {{
                font-size: 12px;
                text-align: center;
                color: #888;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <h1>Permintaan Reset Password</h1>
            <p>Hai,</p>
            <p>Kami menerima permintaan untuk mereset password Anda. Gunakan kode OTP di bawah untuk mengganti password Anda:</p>
            <span class="otp">{otp}</span>
            <p>OTP ini berlaku selama 5 menit. Setelah itu, kode ini akan kadaluarsa dan Anda perlu meminta OTP baru.</p>
            <p>Jika Anda tidak meminta reset password, abaikan email ini.</p>
            <div class="footer">
                <p>Salam,<br>Tim Kami</p>
                <p>Jika Anda membutuhkan bantuan, silakan hubungi kami.</p>
            </div>
        </div>
    </body>
    </html>
    """
    # Mengatur MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'html'))  # Menggunakan 'html' sebagai jenis konten

    try:
        # Menghubungkan ke server SMTP Gmail
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Mulai koneksi TLS
            server.login(sender_login_email, sender_password)  # Login ke Gmail
            server.sendmail(sender_email, recipient_email, message.as_string())  # Kirim email
        print("Email OTP berhasil dikirim!")
    except Exception as e:
        print(f"Gagal mengirim email: {e}")
