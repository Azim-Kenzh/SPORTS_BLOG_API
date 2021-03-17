import requests
from bs4 import BeautifulSoup


def get_html(url):
    response = requests.get(url)
    return response.text


list_ = []


def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    product_list = soup.find('div', class_="middle-col")
    products = product_list.find_all('div', class_="category-item last-feed")

    for product in products:
        try:
            title = product.find('div', class_='category-feed-title').find('a').text
        except:
            title = ''
        try:
            photo = 'http://sport.akipress.org'+product.find('div', class_='category-feed-img').find('a').get('href') + product.find('img').get('src')
        except:
            photo = ''

        data = {'title': title, 'photo': photo}

        list_.append(data)
    # write_to_json(list_)
    return list_


def main():
    news_url = 'http://sport.akipress.org/category:82'
    news = get_page_data(get_html(news_url))
    return news