import time
from datetime import datetime, date

from playwright.sync_api import sync_playwright
from loguru import logger

from modules.scripts import (
    GET_AREAS,
    GET_ADVERTS_DATES,
    GET_ADVERTS_IDS,
    GET_CHARS,
    GET_DESCR,
    GET_PRICE,
    GET_TITLE,
    GET_YEAR,
)

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


def safe_eval(page, expression: str, field_name: str):
    """Выполняет JS и безопасно возвращает результат"""
    try:
        return page.evaluate(expression=expression)
    except Exception as e:
        logger.debug(f"[{field_name}] Не найден элемент → {e}")
        return None


class ChromeBrowser:
    def __init__(self, headless: bool = True):
        self.base_url = "https://kolesa.kz/cars/"
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        self.page = self.browser.new_page()
        self.page.set_default_timeout(60000)
        logger.info("Google Chrome открыт")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Google Chrome закрыт")

    def get_cities(self):
        self.page.goto(url=self.base_url)
        btn = self.page.wait_for_selector(selector=".FilterGroup__toggle")
        if btn:
            btn.click()
        else:
            logger.error("Кнопка выбора городов не найдена")
        time.sleep(3)
        cities_block = self.page.evaluate(expression=GET_AREAS)
        logger.info(f"Cities block: {cities_block}")
        return cities_block

    def get_adverts(self, city_alias: str, parse_date: date):
        data = {}
        page_num = 1
        while True:
            page_arg = "" if page_num == 1 else f"?page={page_num}"
            url = f"{self.base_url}{city_alias}/{page_arg}"
            self.page.goto(url=url)

            ids = self.page.evaluate(expression=GET_ADVERTS_IDS)
            dates = self.page.evaluate(expression=GET_ADVERTS_DATES)

            for i, item in enumerate(ids):
                try:
                    temp: str = dates[i]
                    day, month = temp.split(" ")
                    date_to_compare = date(
                        year=datetime.now().year,
                        month=MONTHS.get(month),
                        day=int(day),
                    )
                    if date_to_compare >= parse_date:
                        data[int(item)] = date_to_compare
                except Exception as e:
                    logger.warning(f"Ошибка при обработке даты {dates[i]}: {e}")

            page_num += 1
            if page_num > 5:
                break
            time.sleep(5)
        return data

    def get_full_data(self, advert_id: int):
        url = f"https://kolesa.kz/a/show/{advert_id}"
        self.page.goto(url=url)

        title = safe_eval(self.page, GET_TITLE, "title")
        year_of_issue = safe_eval(self.page, GET_YEAR, "year")
        description = safe_eval(self.page, GET_DESCR, "description")
        characteristics = safe_eval(self.page, GET_CHARS, "characteristics")
        temp_price = safe_eval(self.page, GET_PRICE, "price")

        price = None
        if temp_price:
            try:
                price = int(
                    temp_price.split(" ")[0].replace("\xa0", "").replace(" ", "")
                )
            except Exception as e:
                logger.warning(f"[price] Ошибка обработки '{temp_price}': {e}")

        data = {
            "title": title,
            "year_of_issue": int(year_of_issue) if year_of_issue else None,
            "description": description,
            "characteristics": characteristics,
            "price": price,
        }

        logger.info(f"[Advert {advert_id}] Собраны данные: {data}")
        return data

    def collect_links(self, advert_id: int):
        url = f"https://kolesa.kz/a/show/{advert_id}"
        self.page.goto(url=url)
        try:
            links = self.page.eval_on_selector_all(
                "img", "elements => elements.map(e => e.src)"
            )
            logger.info(f"[{advert_id}] найдено {len(links)} картинок")
            return links
        except Exception as e:
            logger.error(f"[{advert_id}] Ошибка получения ссылок: {e}")
            return []
