import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
from collections import Counter
import seaborn as sns
import re
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import string
import calendar

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["senja"]
collection = db["tari_article"]

# 🔄 Update kolom 'source' dari URL jika belum ada
collection.update_many(
    {"url": {"$regex": "detik\\.com"}, "source": {"$exists": False}},
    {"$set": {"source": "detik"}}
)
collection.update_many(
    {"url": {"$regex": "kompas\\.com"}, "source": {"$exists": False}},
    {"$set": {"source": "kompas"}}
)

# Ambil data
articles = collection.find()
df = pd.DataFrame(list(articles))

# Memastikan kolom 'source' terisi
df['source'] = df['source'].fillna('kompas')  # fallback

# Filter hanya untuk sumber 'kompas-tv' dan 'detik'
allowed_sources = ['kompas-tv', 'detik']
df = df[df['source'].isin(allowed_sources)]

# Sidebar filter (masih bisa memilih tapi hanya 2 opsi)
st.sidebar.header("Filter")
available_sources = df['source'].dropna().unique().tolist()
selected_sources = st.sidebar.multiselect("Pilih Sumber Artikel", available_sources, default=available_sources)
df = df[df['source'].isin(selected_sources)]

# Judul utama
st.title('Visualisasi Data Artikel Tari Tradisional')

# Pra-pemrosesan tanggal
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

# 1. Jumlah Artikel per Bulan
st.subheader("1. Jumlah Artikel per Bulan")
article_per_month = df.groupby('month').size()
article_per_month.index = article_per_month.index.map(lambda x: calendar.month_name[int(x)])
month_order = list(calendar.month_name)[1:]
article_per_month = article_per_month.reindex(month_order).dropna()

fig1, ax1 = plt.subplots()
article_per_month.plot(kind='bar', ax=ax1)
ax1.set_title('Jumlah Artikel per Bulan')
ax1.set_xlabel('Bulan')
ax1.set_ylabel('Jumlah Artikel')
st.pyplot(fig1)

# 2. WordCloud dari Kata-Kata yang Sering Muncul
st.subheader("2. WordCloud Kata-Kata yang Sering Muncul dalam Artikel")

nltk.download('stopwords')
stop_words = set(stopwords.words('indonesian'))

if 'title' in df.columns or 'content' in df.columns:
    combined_text = df['title'].fillna('') + ' ' + df['content'].fillna('')
    text_data = ' '.join(combined_text.tolist()).lower()
    text_data_clean = text_data.translate(str.maketrans('', '', string.punctuation))
    words = text_data_clean.split()
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    word_freq = ' '.join(filtered_words)

    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='magma').generate(word_freq)
    fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
    ax_wc.imshow(wordcloud, interpolation='bilinear')
    ax_wc.axis('off')
    st.pyplot(fig_wc)
else:
    st.warning("Kolom 'title' dan 'content' tidak tersedia.")

# 3. Jenis Tari yang Paling Populer Berdasarkan Kemunculan Kata
st.subheader("3. Jenis Tari Paling Sering Disebut")

if 'title' in df.columns or 'content' in df.columns:
    text_data = df['title'].fillna('') + ' ' + df['content'].fillna('')
    text_data = ' '.join(text_data.tolist()).lower()
    tari_matches = re.findall(r'tari\s+([a-zA-Z\-]+)', text_data)
    valid_tari_names = {
        'jaipong', 'saman', 'piring', 'topeng', 'gambyong', 'kecak', 'serimpi',
        'bedhaya', 'reog', 'ronggeng', 'lengger', 'tortor', 'tandak', 'zapin',
        'tari', 'seblang', 'seudati', 'merak', 'payung', 'legong', 'cakalele'
    }
    tari_filtered = [t for t in tari_matches if t in valid_tari_names]
    tari_counts = Counter(tari_filtered).most_common(10)

    if tari_counts:
        tari_df = pd.DataFrame(tari_counts, columns=['Nama Tari', 'Frekuensi'])
        fig5, ax5 = plt.subplots()
        sns.barplot(x='Frekuensi', y='Nama Tari', data=tari_df, ax=ax5, palette='mako')
        ax5.set_title("10 Jenis Tari Paling Sering Disebut dalam Artikel")
        st.pyplot(fig5)
    else:
        st.info("Tidak ditemukan nama tari dalam artikel.")
else:
    st.warning("Kolom 'title' dan 'content' tidak tersedia.")
