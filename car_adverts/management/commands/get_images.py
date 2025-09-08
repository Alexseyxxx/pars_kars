import uuid
import requests
from loguru import logger
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from modules.browser import ChromeBrowser
from car_adverts.models import Advert, AdvertImage


class Command(BaseCommand):
    help = "Загрузка изображений для объявлений"

    def handle(self, *args, **options):
        adverts = Advert.objects.filter(advert_images__isnull=True)
        logger.info(f"Найдено {adverts.count()} объявлений без картинок")

        for advert in adverts[:5]:
            links = self.get_data(advert_id=advert.pk)
            if not links:
                logger.warning(f"Нет ссылок для объявления {advert.pk}")
                continue

            for link in links:
                img_bytes = self.processing_link(link=link)
                if not img_bytes:
                    logger.error(f"Ошибка загрузки {link}")
                    continue

                img_file = ContentFile(img_bytes, name=f"{uuid.uuid4()}.jpg")
                AdvertImage.objects.create(image=img_file, advert=advert)
                logger.info(f"Картинка сохранена для объявления {advert.pk}")

    def get_data(self, advert_id: int):
        """
        Здесь должен быть код, который получает ссылки на изображения.
        Пока заглушка.
        """
        return [
            "/images/svg-convert/splide-arrow-next.svg"
        ]

    def processing_link(self, link: str):
        """
        Скачивает картинку по ссылке и возвращает байты.
        """
        try:
            response = requests.get(link, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Ошибка загрузки {link}: {e}")
            return None
