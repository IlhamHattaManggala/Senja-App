from flask import render_template
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017")  # Menghubungkan ke MongoDB lokal
db = client["senja"]  # Ganti dengan nama database kamu
collection = db["tari_article"]  # Ganti dengan nama koleksi yang kamu pakai

# Fungsi untuk menangani visualisasi
def generate_visualizations():
    # Ambil data dari MongoDB
    articles = collection.find()
    df = pd.DataFrame(list(articles))

    # Visualisasi 1: Jumlah Artikel per Bulan
    df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Pastikan kolom 'date' ada
    df['month'] = df['date'].dt.month
    article_per_month = df.groupby('month').size()

    fig1, ax1 = plt.subplots(figsize=(8, 6))
    article_per_month.plot(kind='bar', ax=ax1)
    ax1.set_title('Jumlah Artikel per Bulan')
    ax1.set_xlabel('Bulan')
    ax1.set_ylabel('Jumlah Artikel')
    fig1.savefig(os.path.join('static', 'img', 'visualisasi', 'month_bar.png'))

    # Visualisasi 2: Jumlah Artikel Berdasarkan Tanggal
    article_per_day = df.groupby(df['date'].dt.date).size()
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    article_per_day.plot(kind='line', ax=ax2)
    ax2.set_title('Jumlah Artikel Berdasarkan Tanggal')
    ax2.set_xlabel('Tanggal')
    ax2.set_ylabel('Jumlah Artikel')
    fig2.savefig(os.path.join('static', 'img', 'visualisasi', 'day_line.png'))

    # Visualisasi 3: Tren Jumlah Artikel per Tahun
    df['year'] = df['date'].dt.year
    article_per_year = df.groupby('year').size()
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    article_per_year.plot(kind='line', ax=ax3)
    ax3.set_title('Tren Jumlah Artikel per Tahun')
    ax3.set_xlabel('Tahun')
    ax3.set_ylabel('Jumlah Artikel')
    fig3.savefig(os.path.join('static', 'img', 'visualisasi', 'year_trend.png'))

    # Visualisasi 4: Jumlah Artikel per Daerah (Tarian dari daerah mana saja)
    if 'region' in df.columns:  # Pastikan ada kolom 'region' untuk daerah
        region_count = df['region'].value_counts()
        fig4, ax4 = plt.subplots(figsize=(8, 6))
        region_count.plot(kind='bar', ax=ax4)
        ax4.set_title('Jumlah Artikel Berdasarkan Daerah')
        ax4.set_xlabel('Daerah')
        ax4.set_ylabel('Jumlah Artikel')
        fig4.savefig(os.path.join('static', 'img', 'visualisasi', 'region_count.png'))

    # Visualisasi 5: Hubungan Antara Daerah dan Jenis Tari (Jika ada data ini)
    if 'region' in df.columns and 'dance_type' in df.columns:
        plt.figure(figsize=(10, 6))
        sns.countplot(x='region', hue='dance_type', data=df)
        plt.title('Hubungan Antara Daerah dan Jenis Tari')
        plt.xlabel('Daerah')
        plt.ylabel('Jumlah Artikel')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join('static', 'img', 'visualisasi', 'region_dance_type.png'))

# Fungsi untuk merender halaman visualisasi
def render_visualizations():
    # Jalankan fungsi untuk menghasilkan visualisasi
    generate_visualizations()
    
    # Mengembalikan hasil ke template HTML
    return render_template('visualisasi.html')
