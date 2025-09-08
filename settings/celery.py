import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

app = Celery("povtor")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["car_adverts"])
app.conf.timezone = "Asia/Almaty"
