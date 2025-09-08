from django.db.models import Q
from django.core.management.base import BaseCommand
from loguru import logger
import time

from modules.browser import ChromeBrowser
from car_adverts.models import Advert


class Command(BaseCommand):
    help = "Fill adverts with missing data"

    def handle(self, *args, **options):
        # Выбираем объявления с пустыми или отсутствующими полями
        adverts = list(
            Advert.objects.filter(
                Q(title__isnull=True) | Q(title="") |
                Q(description__isnull=True) | Q(description="") |
                Q(price__isnull=True)
            )
        )

        if not adverts:
            logger.info("Нет объявлений для обработки")
            return

        logger.info(f"Найдено {len(adverts)} объявлений для обработки")

        items_to_update = []

        with ChromeBrowser(headless=True) as browser:
            for advert in adverts:
                try:
                    time.sleep(2)  # пауза, чтобы не банили
                    data = browser.get_full_data(advert_id=advert.pk)
                    if not data:
                        continue

                    updated_fields = []
                    for key, value in data.items():
                        if value not in (None, "", {}):
                            setattr(advert, key, value)
                            updated_fields.append(key)

                    if updated_fields:
                        items_to_update.append(advert)
                        logger.info(f"[Advert {advert.pk}] Обновлены поля: {', '.join(updated_fields)}")
                    else:
                        logger.info(f"[Advert {advert.pk}] Нет новых данных для обновления")

                except Exception as e:
                    logger.error(f"[Advert {advert.pk}] Ошибка обработки: {e}")
                    continue

        if items_to_update:
            # Определяем все поля, которые реально обновились
            fields_to_update = set()
            for obj in items_to_update:
                for field in obj.__dict__.keys():
                    if field not in ("_state", "id", "pk"):
                        fields_to_update.add(field)

            logger.info(f"Обновляем поля: {', '.join(fields_to_update)}")
            Advert.objects.bulk_update(items_to_update, list(fields_to_update))
            logger.info(f"Обновлено {len(items_to_update)} объявлений")
        else:
            logger.info("Нет объявлений для обновления")


# import time

# from loguru import logger
# from django.core.management.base import BaseCommand

# from modules.browser import ChromeBrowser
# from car_adverts.models import Advert


# class Command(BaseCommand):
#     def processing(self, advert_id: int):
#         with ChromeBrowser() as browser:
#             data = browser.get_full_data(advert_id=advert_id)
#         return data

#     def handle(self, *args, **options):
#         adverts = Advert.objects.filter(title__isnull=True)
#         if not adverts:
#             logger.info("There are no adverts to processing")
#             return
#         logger.info(f"Founded {len(adverts)} adverts")
#         items = []
#         fields = []
#         for advert in adverts:
#             time.sleep(5)
#             data = self.processing(advert_id=advert.pk)
#             if not data:
#                 continue
#             for key, value in data.items():
#                 setattr(advert, key, value)
#             if not fields:
#                 for key in data.keys():
#                     fields.append(key)
#             items.append(advert)
#         logger.info(f"Fields for update: {','.join(fields)}")
#         Advert.objects.bulk_update(objs=items, fields=fields)