from rest_framework import serializers
from .models import Advert, City, AdvertImage

class AdvertImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvertImage
        fields = ["id", "image"]

class AdvertSerializer(serializers.ModelSerializer):
    advert_images = AdvertImageSerializer(many=True, read_only=True)
    city = serializers.StringRelatedField()

    class Meta:
        model = Advert
        fields = [
            "id",
            "title",
            "price",
            "description",
            "year_of_issue",
            "characteristics",
            "city",
            "publication_date",
            "advert_images",
        ]

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "title", "alias"]
