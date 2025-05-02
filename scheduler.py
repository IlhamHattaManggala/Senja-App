import schedule
import time

# Import konfigurasi dan inisialisasi Flask app
from flask import Flask
from config import configClass
from db import mongo, init_mongo
from controller.ScrappingController import run_scraping

# Inisialisasi Flask App
app = Flask(__name__)
app.config.from_object(configClass)

# Inisialisasi koneksi MongoDB
init_mongo(app)

# Aktifkan app context Flask supaya mongo.db bisa digunakan
with app.app_context():
    # Jadwalkan scraping setiap hari pukul 10:23
    schedule.every().day.at("10:34").do(run_scraping)

    print("Penjadwalan dimulai, menunggu sampai 10:34 untuk menjalankan proses scraping...")

    while True:
        schedule.run_pending()
        print("Scheduler sedang menunggu tugas selanjutnya...")
        time.sleep(60)
