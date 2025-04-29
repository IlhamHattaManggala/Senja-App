import requests
from bs4 import BeautifulSoup
import datetime
import re
from db import mongo
from config import configClass

# Fungsi untuk membersihkan konten HTML dari elemen yang tidak relevan
def clean_html_content(content_div):
    # Hapus elemen-elemen yang tidak relevan seperti iklan, video, dsb
    for unwanted in content_div.find_all(['aside', 'figure', 'div', 'section', 'iframe']):
        unwanted.decompose()  # Menghapus elemen tersebut
    
    # Ambil hanya teks dalam elemen <p>
    paragraphs = content_div.find_all('p')
    return '\n\n'.join(p.get_text(strip=True) for p in paragraphs)

# Fungsi untuk mengambil gambar
def get_image_url(article_soup):
    image_tag = article_soup.find('div', class_='detail__media').find('img')
    if image_tag and image_tag.has_attr('src'):
        return image_tag['src']
    return None

# Fungsi scraping
def scrape_tari_articles():
    today = datetime.date.today()  # Ambil tanggal hari ini
    tari_article = mongo.db[configClass.TARI_ARTICLE_COLLECTION]

    url = "https://www.detik.com/search/searchall?query=tari"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')

        for article in articles:
            title = article.find('h3')
            if title:
                title_text = title.get_text()
                link = article.find('a')['href']

                print(f"Judul artikel: {title_text}")
                print(f"Link artikel: {link}")

                article_response = requests.get(link)
                if article_response.status_code == 200:
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')

                    # Ambil tanggal artikel
                    date_tag = (
                        article_soup.find('div', class_='detail__date') or
                        article_soup.find('span', class_='date') or
                        article_soup.find('time')
                    )

                    if date_tag:
                        raw_date = date_tag.get_text().strip()
                        match = re.search(r'\d{1,2} \w{3,9} \d{4}', raw_date)

                        if match:
                            try:
                                article_date = datetime.datetime.strptime(match.group(), "%d %b %Y").date()
                            except ValueError:
                                print(f"Tanggal tidak valid: {match.group()}")
                                continue
                        else:
                            print(f"Tidak bisa ekstrak tanggal dari: {raw_date}")
                            continue

                        # Cek apakah tanggal artikel == hari ini
                        if article_date == today:
                            if tari_article.find_one({'url': link}):
                                print(f"Artikel sudah ada: {link}")
                                continue

                            # Ambil isi artikel dan bersihkan
                            content_div = article_soup.find('div', class_='detail__body-text') or \
                                          article_soup.find('div', class_='detail_text')
                            if content_div:
                                content_text = clean_html_content(content_div)
                            else:
                                content_text = ''

                            # Ambil gambar artikel
                            image_url = get_image_url(article_soup)

                            document = {
                                'title': title_text,
                                'url': link,
                                'content': content_text,
                                'date': article_date.isoformat(),
                                'image_url': image_url  # Menyimpan URL gambar
                            }

                            tari_article.insert_one(document)
                            print(f"Artikel disimpan: {title_text}")
                            if image_url:
                                print(f"Gambar disimpan: {image_url}")
                        else:
                            print(f"Artikel di luar tanggal hari ini: {title_text}")
                    else:
                        print("Tanggal artikel tidak ditemukan.")
                else:
                    print(f"Gagal akses artikel: {link}")
                print('-' * 50)
    else:
        print("Gagal akses halaman pencarian.")
