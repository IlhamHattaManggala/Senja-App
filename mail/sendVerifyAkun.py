import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import ConfigClass

def send_verify_email(email, otp):
    sender_email = ConfigClass.MAIL_DEFAULT_SENDER  # Ganti dengan email pengirim
    sender_login_email = ConfigClass.MAIL_USERNAME
    sender_password = ConfigClass.MAIL_PASSWORD  # Ganti dengan App Password Gmail
    recipient_email = email

    # Konten email dengan format HTML
    subject = "Verifikasi Akun Senja App"
    body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f0f2f5;
                margin: 0;
                padding: 0;
            }}

            .email-wrapper {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 12px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
                overflow: hidden;
                border: 1px solid #e0e0e0;
            }}

            .header {{
                background-color: #4CAF50;
                color: white;
                text-align: center;
                padding: 30px 20px;
            }}

            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}

            .content {{
                padding: 30px 25px;
                color: #333;
                font-size: 16px;
                line-height: 1.6;
            }}

            .content p {{
                margin-bottom: 16px;
            }}

            .otp-card {{
                background-color: #e9f5ff;
                border: 1px solid #b3d6f7;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                margin: 30px 0;
                box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
            }}

            .otp-code {{
                font-size: 24px;
                font-weight: bold;
                color: #007BFF;
                letter-spacing: 4px;
            }}

            .footer {{
                text-align: center;
                font-size: 13px;
                color: #888;
                padding: 20px;
                background-color: #fafafa;
                border-top: 1px solid #eee;
            }}

            .footer strong {{
                color: #333;
            }}
        </style>
    </head>
    <body>
        <div class="email-wrapper">
            <div class="header">
                <h1>Verifikasi Akun Anda</h1>
            </div>
            <div class="content">
                <p>Hai,</p>
                <p>Terima kasih telah mendaftar. Untuk mengaktifkan akun Anda, silakan gunakan kode OTP berikut:</p>

                <!-- OTP Card -->
                <div class="otp-card">
                    <div class="otp-code">{otp}</div>
                </div>

                <p>Kode OTP ini berlaku selama <strong>5 menit</strong>. Setelah itu, kode akan kadaluarsa dan Anda perlu meminta OTP baru.</p>
                <p>Jika Anda tidak merasa melakukan pendaftaran ini, silakan abaikan email ini.</p>
            </div>
            <div class="footer">
                <p>Salam hangat,<br><strong>Tim Kami</strong></p>
                <p>Butuh bantuan? Hubungi kami melalui email atau pusat bantuan.</p>
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
