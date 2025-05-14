import requests
from bs4 import BeautifulSoup
import datetime
import re
import pymongo
from urllib.parse import urlparse
from db import mongo  
from config import configClass  

def clean_html_content(content_div):
    for unwanted in content_div.find_all(['aside', 'figure', 'div', 'section', 'iframe']):
        unwanted.decompose()
    paragraphs = content_div.find_all('p')
    return '\n\n'.join(p.get_text(strip=True) for p in paragraphs)

def get_image_url(article_soup):
    image_tag = article_soup.find('div', class_='detail__media')
    if image_tag:
        img = image_tag.find('img')
        if img and img.has_attr('src'):
            return img['src']
    return None

def scrape_tari_articles():
    if mongo.db is None:
        print("Koneksi MongoDB gagal!")
        return

    tari_article = mongo.db[configClass.TARI_ARTICLE_COLLECTION]
    base_urls = [
<<<<<<< HEAD
        "https://www.kompas.tv/search?q=tari&gsc.page=",  # Mulai dari Kompas TV
        "https://www.detik.com/search/searchall?query=tari&page="  # Detik setelahnya
    ]
    total_saved = 0

    # Mulai scraping dari Kompas TV dulu
=======
        "https://www.detik.com/search/searchall?query=tari&page=",
        "https://www.kompas.tv/search?q=tari#gsc.tab=0&gsc.q=tari&gsc.page="
    ]
    total_saved = 0

    # Hitung tanggal kemarin
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

>>>>>>> 1a0098daa81f648d48da525b022c826e9c9e7a3d
    for base_url in base_urls:
        page_num = 1
        while True:
            url = base_url + str(page_num)
            response = requests.get(url)

            # Jika Kompas TV error (misalnya 404, timeout), lanjut ke Detik
            if response.status_code != 200:
                print(f"Gagal akses halaman {url} dari Kompas TV, lanjutkan ke Detik.")
                if "kompas.tv" in base_url:
                    break  # Keluar dari loop Kompas TV, lanjut ke Detik
                else:
                    continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # Deteksi apakah ini halaman dari Kompas TV
            is_kompas = "kompas.tv" in base_url

            if is_kompas:
                articles = soup.select('div.gsc-webResult.gsc-result')
            else:
                articles = soup.find_all('article')

            if not articles:
                print("Tidak ada artikel lebih lanjut.")
                break

            for article in articles:
<<<<<<< HEAD
                if is_kompas:
                    link_tag = article.select_one('a.gs-title')
                    if not link_tag or not link_tag.has_attr('href'):
                        continue
                    link = link_tag['href']
                    title_text = link_tag.get_text().strip()
                else:
                    title_tag = article.find('h3')
                    if not title_tag:
                        continue
                    title_text = title_tag.get_text().strip()
                    link_tag = article.find('a')
                    if not link_tag or not link_tag.has_attr('href'):
                        continue
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = "https://www.detik.com" + link

                # Cek apakah artikel sudah ada
                if tari_article.find_one({'url': link}):
                    print(f"Artikel sudah ada: {link}")
                    continue
=======
                title = article.find('h3')
                if title:
                    title_text = title.get_text().strip()
                    link = article.find('a')['href']

                    if not link.startswith('http'):
                        link = "https://www.detik.com" + link

                    if tari_article.find_one({'url': link}):
                        print(f"Artikel sudah ada: {link}")
                        continue
>>>>>>> 1a0098daa81f648d48da525b022c826e9c9e7a3d

                # Ambil konten artikel
                article_response = requests.get(link)
                if article_response.status_code != 200:
                    continue

                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                # Tanggal
                date_tag = article_soup.find('div', class_='detail__date') or article_soup.find('span', class_='date') or article_soup.find('time')
                if date_tag:
                    raw_date = date_tag.get_text().strip()
                    match = re.search(r'\d{1,2} \w{3,9} \d{4}', raw_date)
                    if match:
                        try:
                            article_date = datetime.datetime.strptime(match.group(), "%d %b %Y").date()
                        except ValueError:
                            try:
                                article_date = datetime.datetime.strptime(match.group(), "%d %B %Y").date()
                            except:
                                article_date = None
                    else:
                        article_date = None
                else:
                    article_date = None

<<<<<<< HEAD
                # Konten
                content_div = article_soup.find('div', class_='detail__body-text') or \
                              article_soup.find('div', class_='detail_text') or \
                              article_soup.find('div', class_='article__content')
                content_text = clean_html_content(content_div) if content_div else ''
=======
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
>>>>>>> 1a0098daa81f648d48da525b022c826e9c9e7a3d

                # Gambar
                image_url = get_image_url(article_soup)

<<<<<<< HEAD
                # Source
                parsed_url = urlparse(link)
                domain = parsed_url.netloc.replace("www.", "").lower()
                if "detik" in domain:
                    source = "detik"
                elif "kompas" in domain:
                    source = "kompas"
                else:
                    source = domain
=======
                        document = {
                            'title': title_text,
                            'url': link,
                            'content': content_text,
                            'date': article_date.isoformat() if article_date else None,
                            'image_url': image_url
                        }
>>>>>>> 1a0098daa81f648d48da525b022c826e9c9e7a3d

                document = {
                    'title': title_text,
                    'url': link,
                    'content': content_text,
                    'date': article_date.isoformat() if article_date else None,
                    'image_url': image_url,
                    'source': source
                }

<<<<<<< HEAD
                tari_article.insert_one(document)
                total_saved += 1
                print(f"Artikel disimpan: {title_text}")
                if image_url:
                    print(f"  ➤ Gambar: {image_url}")

            print(f"Total artikel disimpan di halaman {page_num}: {total_saved}")
=======
            print(f"Total artikel yang berhasil disimpan di halaman {page_num}: {total_saved}")
>>>>>>> 1a0098daa81f648d48da525b022c826e9c9e7a3d
            page_num += 1

def run_scraping():
    print("Memulai proses scraping...")
    scrape_tari_articles()
    print("Proses scraping selesai!")