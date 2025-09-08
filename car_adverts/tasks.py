from datetime import date
import time
import uuid

import requests
from celery import Task
from loguru import logger
from django.core.files.base import ContentFile

from settings import celery_app
from modules.browser import ChromeBrowser
from car_adverts.models import City, Advert, AdvertImage


class GetAdvertIds(Task):
    name = "get-advert-ids"
    time_limit = 60 * 30
    acks_late = True
    
    def run(self, parse_date: date, city_alias: str):
        """Использовать модуль get_adverts."""
        with ChromeBrowser(headless=False) as browser:
            adverts = browser.get_adverts(
                parse_date=parse_date,
                city_alias=city_alias,
            )

        city = City.objects.get(alias=city_alias)
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

    def on_success(self, retval, task_id, args, kwargs):
        FillAdverts().apply_async()


class FillAdverts(Task):
    name = "fill-adverts"
    time_limit = 3600
    acks_late = True

    def processing(self, advert_id: int):
        with ChromeBrowser() as browser:
            data = browser.get_full_data(advert_id=advert_id)
        return data

    def run(self):
        """Использовать модуль fill_adverts и поставить в очередь следующую задачу"""
        adverts = Advert.objects.filter(title__isnull=True)
        if not adverts:
            logger.info("There are no adverts to processing")
            return
        logger.debug(f"Founded {len(adverts)} adverts")
        items = []
        fields = []
        for advert in adverts:
            time.sleep(5)
            data = self.processing(advert_id=advert.pk)
            if not data:
                continue
            for key, value in data.items():
                setattr(advert, key, value)
            if not fields:
                for key in data.keys():
                    fields.append(key)
            items.append(advert)
        logger.debug(f"Fields for update: {','.join(fields)}")
        Advert.objects.bulk_update(objs=items, fields=fields)

    def on_success(self, retval, task_id, args, kwargs):
        GetImages().apply_async()


class GetImages(Task):
    name = "get-images"
    time_limit = 3600
    acks_late = True

    def get_data(self, advert_id: int):
        with ChromeBrowser() as browser:
            links = browser.collect_links(advert_id=advert_id)
        return links
    
    def processing_link(self, link: str) -> bytes | None:
        try:
            response = requests.get(url=link)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Cannot open image: {e}")
            return None

    def run(self):
        """Использовать get_images"""
        adverts = Advert.objects.filter(advert_images__isnull=True)
        for advert in adverts:
            time.sleep(5)
            links = self.get_data(advert_id=advert.pk)
            for link in links:
                img_bytes = self.processing_link(link=link)
                if not img_bytes:
                    continue
                img_file = ContentFile(content=img_bytes, name=f"{uuid.uuid4()}.jpg")
                AdvertImage.objects.create(image=img_file, advert=advert)


celery_app.register_task(task=GetAdvertIds())
celery_app.register_task(task=FillAdverts())
celery_app.register_task(task=GetImages())