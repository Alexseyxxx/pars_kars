from django.contrib import admin

from car_adverts.models import City, Advert, AdvertImage


admin.site.register((City, Advert, AdvertImage))