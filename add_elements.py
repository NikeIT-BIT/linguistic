from connect import forecast
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Базовый URL
base_url = "https://os34.ru"


def get_absolute_url(relative_url):
    """Преобразует относительную ссылку в абсолютную."""
    return urljoin(base_url, relative_url)


def parse_page(url):
    """Парсит страницу и записывает данные в базу данных."""
    response = requests.get(url)
    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.content, "html.parser")

    # Находим все заголовки
    titles = soup.find_all("h3", class_="b-section-item__title")

    # Перебираем заголовки

    for title in titles:
        title_text = title.text.strip()
        news_link = get_absolute_url(title.find("a")["href"])
        # &action=navigation&id=section_53e935c&isAjax=Y
        subpage_response = requests.get(news_link)
        print(news_link)
        if subpage_response.status_code != 200:
            continue

        subpage_soup = BeautifulSoup(subpage_response.content, "html.parser")

        # Находим все элементы <div> с классом "b-news-detail-body"
        news_detail_divs = subpage_soup.find_all('div', class_='b-news-detail-body')

        # Извлекаем текст из каждого найденного элемента
        news_text = ''
        for news_detail_div in news_detail_divs:
            news_text = news_detail_div.get_text(strip=True)

        # Ищем тег <time> с классом "b-meta-item"
        publication_date_tag = subpage_soup.find("time", class_="b-meta-item")
        publication_date = publication_date_tag.get("datetime", "") if publication_date_tag else ""
        # Проверяем наличие даты перед сохранением в базу данных
        if publication_date:
            # Записываем данные в базу данных
            forecast.put_item(
                Item={
                    'title': title_text,
                    'date': publication_date,
                    'link': news_link,
                    'text': news_text,
                }
            )


# Парсим главную страницу
main_page_url = base_url
main_page_response = requests.get(main_page_url)
main_page_soup = BeautifulSoup(main_page_response.content, "html.parser")


# Парсим подстраницы
menu_items = main_page_soup.find_all("div", class_="b-main-menu-item has-dropdown")
for menu_item in menu_items:
    relative_link = menu_item.find("a")["href"]
    subpage_url = get_absolute_url(relative_link)

    # Проверяем, нужно ли пропустить обработку текущей подстраницы
    if subpage_url in excluded_links:
        print(f"Skipping {subpage_url}...")
        continue
    for pagen in range(300, 500):
        print(subpage_url + f'?PAGEN_2={pagen}&action=navigation&id=section_53e935c&isAjax=Y')
        parse_page(subpage_url + f'?PAGEN_2={pagen}&action=navigation&id=section_53e935c&isAjax=Y')
