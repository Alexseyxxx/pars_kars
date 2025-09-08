#дз 
#headless=False → браузер видно, открывается окно и можно наблюдать, что он делает.
#headless=True → браузер работает «невидимо», окна нет, всё происходит в фоне.

# from loguru import logger
# from django.core.management.base import BaseCommand

# from car_adverts.models import City
# from modules.browser import ChromeBrowser


# class Command(BaseCommand):
#     help = "Парсинг и сохранение списка городов"

#     def add_arguments(self, parser):
#         parser.add_argument(
#             "--headless",
#             action="store_true",
#             help="Запуск браузера в headless-режиме (по умолчанию окно открыто)",
#         )

#     def handle(self, *args, **options):
#         headless = options["headless"]
#         logger.info(f"Begin generate cities (headless={headless})")

#         cities = []
#         with ChromeBrowser(headless=headless) as browser:
#             cities.extend(browser.get_cities())

#         if not cities:
#             logger.error("There are no cities")
#             return

#         objs = []
#         for city in cities:
#             if not city.get("alias"):
#                 continue
#             objs.append(
#                 City(title=city.get("label"), alias=city.get("alias"))
#             )

#         created = City.objects.bulk_create(
#             objs, batch_size=100, ignore_conflicts=True
#         )

#         logger.info(f"✅ Добавлено {len(created)} новых городов из {len(objs)}")
#         logger.info("Generate cities ended")


from loguru import logger
from django.core.management.base import BaseCommand

from car_adverts.models import City
from modules.browser import ChromeBrowser


class Command(BaseCommand):
    def generate(self, *args, **kwargs):
        cities = []
        with ChromeBrowser() as browser:
            cities.extend(browser.get_cities())
        if not cities:
            logger.error("There are no cities")
            return
        objs = []
        for city in cities:
            if not city.get("alias"):
                continue
            objs.append(
                City(title=city.get("label"), alias=city.get("alias"))
            )
        City.objects.bulk_create(
            objs=objs,
            batch_size=100,
            ignore_conflicts=False,
            update_conflicts=False,
        )

    def handle(self, *args, **options):
        logger.info("Begin generate cities")
        self.generate(*args, **options)
        logger.info("Generate cities ended")