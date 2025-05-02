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

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["senja"]
collection = db["tari_article"]

# Ambil data
articles = collection.find()
df = pd.DataFrame(list(articles))

# Pra-pemrosesan
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

st.title('Visualisasi Data Artikel Tari Tradisional')

# 1. Jumlah Artikel per Bulan
st.subheader("1. Jumlah Artikel per Bulan")
article_per_month = df.groupby('month').size()
fig1, ax1 = plt.subplots()
article_per_month.plot(kind='bar', ax=ax1)
ax1.set_title('Jumlah Artikel per Bulan')
ax1.set_xlabel('Bulan')
ax1.set_ylabel('Jumlah Artikel')
st.pyplot(fig1)


#3. WordCloud dari Kata-Kata yang Sering Muncul
st.subheader("2. WordCloud Kata-Kata yang Sering Muncul dalam Artikel")

# Unduh stopwords bahasa Indonesia jika belum
nltk.download('stopwords')
stop_words = set(stopwords.words('indonesian'))

if 'title' in df.columns or 'content' in df.columns:
    combined_text = df['title'].fillna('') + ' ' + df['content'].fillna('')
    text_data = ' '.join(combined_text.tolist()).lower()

    # Hapus tanda baca dan tokenisasi
    text_data_clean = text_data.translate(str.maketrans('', '', string.punctuation))
    words = text_data_clean.split()

    # Filter stopwords
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]

    word_freq = ' '.join(filtered_words)

    # Buat wordcloud
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
    # Gabungkan teks
    text_data = df['title'].fillna('') + ' ' + df['content'].fillna('')
    text_data = ' '.join(text_data.tolist()).lower()

    # Ekstrak nama tari setelah kata 'tari'
    tari_matches = re.findall(r'tari\s+([a-zA-Z\-]+)', text_data)

    # Daftar nama tari yang diakui (bisa ditambah sesuai kebutuhan)
    valid_tari_names = {
        'jaipong', 'saman', 'piring', 'topeng', 'gambyong', 'kecak', 'serimpi',
        'bedhaya', 'reog', 'ronggeng', 'lengger', 'tortor', 'tandak', 'zapin',
        'tari', 'seblang', 'seudati', 'merak', 'payung', 'legong', 'cakalele'
    }

    # Filter hasil hanya nama tari yang valid
    tari_filtered = [t for t in tari_matches if t in valid_tari_names]

    # Hitung frekuensi
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


