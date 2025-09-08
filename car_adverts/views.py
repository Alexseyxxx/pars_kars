from datetime import datetime
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from car_adverts.models import Advert
from .serializers import AdvertSerializer
from car_adverts.tasks import GetAdvertIds


class LaunchTasks(APIView):
    """Запуск задачи GetAdvertIds"""

    def post(self, request):
        city_alias = request.data.get("city_alias")
        date_str = request.data.get("date")

        if not city_alias or not date_str:
            return Response({"error": "city_alias и date обязательны"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            parse_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Неверный формат даты. Используйте YYYY-MM-DD"},
                            status=status.HTTP_400_BAD_REQUEST)

        task = GetAdvertIds().apply_async(args=[parse_date, city_alias])
        return Response({"task_id": task.id, "status": "started"})



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class AdvertsListView(generics.ListAPIView):
    serializer_class = AdvertSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['year_of_issue']
    search_fields = ['title']
    ordering_fields = ['publication_date', 'price']
    ordering = ['-publication_date']

    def get_queryset(self):
        return Advert.objects.select_related('city').prefetch_related('advert_images').all()


class AdvertDetailView(generics.RetrieveAPIView, generics.DestroyAPIView):
    serializer_class = AdvertSerializer

    def get_queryset(self):
        return Advert.objects.select_related('city').prefetch_related('advert_images').all()


# 5. Тестовая точка для запуска fetch_ads_task
class FetchAdsView(APIView):
    def post(self, request):
        city_alias = request.data.get("city_alias")
        pub_date = request.data.get("date")
        task = GetAdvertIds().apply_async(args=[pub_date, city_alias])
        return Response({"task_id": task.id, "status": "started"})
