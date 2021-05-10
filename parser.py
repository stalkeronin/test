import requests
from bs4 import BeautifulSoup
import csv
import subprocess

URL = 'https://auto.ria.com/newauto/marka-lifan/'
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 YaBrowser/20.8.3.132 (beta) Yowser/2.5 Safari/537.36'}
HOST = 'https://auto.ria.com'
FILE = 'cars.csv'

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', class_='page-item mhide')
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1


def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Mark', 'Link', 'usd_cost', 'us_cost', 'City'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['cost_$'], item['cost_UA'], item['city']])


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        cars = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Parsing {page} in {pages_count}')
            html = get_html(URL, params={'page': page})
            cars.extend(get_content(html.text))
        save_file(cars, FILE)
        print(f'Получено {len(cars)} автомобилей')
        subprocess.call(['libreoffice', FILE])
    else:
        print('HttpError')


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='proposition')
    cars = []
    for item in items:
        cars.append({
            'title': item.find('div', class_='proposition_title').get_text(strip=True),
            'link': HOST + item.find('a', class_='proposition_link').get('href'),
            'cost_$': item.find('span', class_='size22').get_text(strip=True),
            'cost_UA': item.find('span', class_='size16').get_text(strip=True),
            'city': item.find('span', class_='item').find_next('span').find_next('span').get_text(strip=True),
        })
    return cars


parse()

