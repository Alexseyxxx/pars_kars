# car_adverts/views.py
from datetime import datetime
from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Advert
from .serializers import AdvertSerializer
from .tasks import GetAdvertIds


class LaunchTasks(APIView):
    """Запуск задачи GetAdvertIds"""
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['city_alias', 'date'],
            properties={
                'city_alias': openapi.Schema(type=openapi.TYPE_STRING, description='Alias города'),
                'date': openapi.Schema(type=openapi.TYPE_STRING, description='Дата в формате YYYY-MM-DD')
            }
        ),
        responses={200: openapi.Response('Task started')}
    )
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
    """Список объявлений с фильтрацией, поиском и пагинацией"""
    serializer_class = AdvertSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['year_of_issue'] 
    search_fields = ['title']  
    ordering_fields = ['publication_date', 'price']  
    ordering = ['-publication_date']

    def get_queryset(self):
       
        return Advert.objects.select_related('city').prefetch_related('advert_images').all()


class AdvertDetailView(generics.RetrieveDestroyAPIView):
    """Просмотр и удаление объявления"""
    serializer_class = AdvertSerializer

    def get_queryset(self):
        return Advert.objects.select_related('city').prefetch_related('advert_images').all()
