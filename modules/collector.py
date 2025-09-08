import time
import random
from datetime import datetime, date

import requests
from bs4 import BeautifulSoup, Tag
from loguru import logger
from fake_useragent import UserAgent

from car_adverts.models import Advert


MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


class AdvertsCollector:
    def __init__(self, date: date, city_alias: str, max_attempts: int = 3):
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "referer": "https://kolesa.kz/",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "x-requested-with": "XMLHttpRequest",
        }
        self.date = date
        self.city = city_alias
        self.max_attempts = max_attempts if max_attempts > 1 else 3
        self.base_url = "https://kolesa.kz/cars/"

    def data_processing(self, content: bytes) -> list[dict]:
        soup = BeautifulSoup(markup=content, features="html.parser")
        car_list: list[Tag] = soup.find_all(
            name="div",
            attrs={"class": "a-list__item"},
        )
        adverts = []
        for item in car_list:
            card = item.find(name="div", attrs={"class": "a-card js__a-card"})
            if not card:
                continue

            advert_id: str = card.attrs.get("data-id")

            # --- дата публикации ---
            public_date = card.find(
                name="span",
                attrs={"class": "a-card__param--date"},
            )
            try:
                day, month = public_date.get_text(strip=True).split(" ")
                date_to_compare = date(
                    year=datetime.now().year,
                    month=MONTHS.get(month),
                    day=int(day),
                )
            except Exception as e:
                logger.debug(f"Дата объявления не распарсилась: {e}")
                continue

            if date_to_compare < self.date:
                continue

            # --- заголовок / описание ---
            title_tag = card.find("h5", class_="a-card__title")
            title = title_tag.get_text(strip=True) if title_tag else None

            # --- цена ---
            price_tag = card.find("span", class_="a-card__price")
            price = price_tag.get_text(strip=True) if price_tag else None

            # --- год ---
            year_tag = card.find("span", class_="a-card__year")
            try:
                year = int(year_tag.get_text(strip=True)) if year_tag else None
            except Exception:
                year = None

            adverts.append({
                "advert_id": int(advert_id),
                "date": date_to_compare,
                "title": title,
                "price": price,
                "year": year,
            })
        return adverts

    def run(self):
        adverts = []
        page = 1
        no_data_counter = 0
        while True:
            self.headers["user-agent"] = UserAgent().random
            page_arg = "" if page == 1 else f"?page={page}"
            url = f"{self.base_url}{self.city}/{page_arg}"
            try:
                logger.debug(f"Make request url: {url}")
                response = requests.get(url=url, headers=self.headers)
                response.raise_for_status()
            except Exception as e:
                logger.error(f"Ошибка запроса: {e}")
                return
            content = response.content
            if not content:
                logger.debug("Пустой ответ от сервера")
                continue
            page += 1
            if page > 5:  # ограничение для теста
                break
            data = self.data_processing(content=content)
            if not data:
                no_data_counter += 1
                logger.debug(f"Нет данных, счётчик {no_data_counter}")
                if no_data_counter > 3:
                    break
            adverts.extend(data)
            delay = random.randint(6, 10)
            logger.debug(f"Пауза {delay} секунд")
            time.sleep(delay)
        return adverts
