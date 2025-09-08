from datetime import date

from loguru import logger
from django.core.management.base import BaseCommand

from modules.browser import ChromeBrowser
from car_adverts.models import Advert, City


class Command(BaseCommand):
    def handle(self, *args, **options):
        city_alias = "region-almatinskaya-oblast"

        # Проверяем, сколько городов с таким alias
        qs = City.objects.filter(alias=city_alias)
        if not qs.exists():
            logger.error(f"Город с alias={city_alias} не найден")
            return

        if qs.count() > 1:
            logger.warning(f"Найдено {qs.count()} городов с alias={city_alias}. Берём первый.")
        city = qs.first()

        with ChromeBrowser(headless=False) as browser:
            adverts = browser.get_adverts(
                parse_date=date(year=2025, month=9, day=1),
                city_alias=city_alias,
            )

        logger.info(f"Data: {adverts}")
        if not adverts:
            logger.error("There is no data")
            return

        items = []
        for key, value in adverts.items():
            items.append(
                Advert(id=key, publication_date=value, city=city)
            )

        logger.info(f"{len(items)} adverts created")
        Advert.objects.bulk_create(
            objs=items, batch_size=200, ignore_conflicts=True
        )

