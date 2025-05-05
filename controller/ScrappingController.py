import requests
from bs4 import BeautifulSoup
import datetime
import re
import pymongo
from db import mongo  
from config import configClass  

# Fungsi untuk membersihkan konten HTML dari elemen yang tidak relevan
def clean_html_content(content_div):
    for unwanted in content_div.find_all(['aside', 'figure', 'div', 'section', 'iframe']):
        unwanted.decompose()
    paragraphs = content_div.find_all('p')
    return '\n\n'.join(p.get_text(strip=True) for p in paragraphs)

# Fungsi untuk mengambil gambar dari artikel
def get_image_url(article_soup):
    image_tag = article_soup.find('div', class_='detail__media')
    if image_tag:
        img = image_tag.find('img')
        if img and img.has_attr('src'):
            return img['src']
    return None

# Fungsi untuk melakukan scraping artikel
def scrape_tari_articles():
    if mongo.db is None:
        print("Koneksi MongoDB gagal!")
        return

    tari_article = mongo.db[configClass.TARI_ARTICLE_COLLECTION]
    base_urls = [
        "https://www.detik.com/search/searchall?query=tari&page=",
        "https://www.kompas.tv/search?q=tari#gsc.tab=0&gsc.q=tari&gsc.page="
    ]
    total_saved = 0

    # Hitung tanggal kemarin
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    for base_url in base_urls:
        page_num = 1
        while True:
            url = base_url + str(page_num)
            response = requests.get(url)

            if response.status_code != 200:
                print("Gagal akses halaman pencarian.")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('article')

            if not articles:
                print("Tidak ada artikel lebih lanjut.")
                break

            for article in articles:
                title = article.find('h3')
                if title:
                    title_text = title.get_text().strip()
                    link = article.find('a')['href']

                    if not link.startswith('http'):
                        link = "https://www.detik.com" + link

                    if tari_article.find_one({'url': link}):
                        print(f"Artikel sudah ada: {link}")
                        continue

                    article_response = requests.get(link)
                    if article_response.status_code == 200:
                        article_soup = BeautifulSoup(article_response.text, 'html.parser')

                        # Ambil tanggal artikel
                        date_tag = article_soup.find('div', class_='detail__date') or article_soup.find('span', class_='date') or article_soup.find('time')
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
                                article_date = None
                        else:
                            article_date = None

                        # Filter hanya artikel dari kemarin
                        if article_date and article_date != yesterday:
                            print(f"Artikel bukan dari kemarin, dilewati: {article_date}")
                            continue

                        # Ambil isi artikel
                        content_div = article_soup.find('div', class_='detail__body-text') or article_soup.find('div', class_='detail_text')
                        if content_div:
                            content_text = clean_html_content(content_div)
                        else:
                            content_text = ''

                        image_url = get_image_url(article_soup)

                        document = {
                            'title': title_text,
                            'url': link,
                            'content': content_text,
                            'date': article_date.isoformat() if article_date else None,
                            'image_url': image_url
                        }

                        tari_article.insert_one(document)
                        total_saved += 1
                        print(f"Artikel disimpan: {title_text}")
                        if image_url:
                            print(f"Gambar disimpan: {image_url}")

            print(f"Total artikel yang berhasil disimpan di halaman {page_num}: {total_saved}")
            page_num += 1

# Fungsi untuk menjalankan proses scraping
def run_scraping():
    print("Memulai proses scraping...")
    scrape_tari_articles()
    print("Proses scraping selesai!")
