from django.contrib import admin
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from car_adverts.views import LaunchTasks, AdvertsListView, AdvertDetailView, FetchAdsView

schema_view = get_schema_view(
   openapi.Info(
      title="Car Adverts API",
      default_version='v1',
      description="API для работы с объявлениями",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("swagger/", schema_view.with_ui('swagger', cache_timeout=0), name="schema-swagger-ui"),
    path("launch-tasks/", LaunchTasks.as_view(), name="launch-tasks"),
    path("adverts/", AdvertsListView.as_view(), name="adverts-list"),
    path("adverts/<int:pk>/", AdvertDetailView.as_view(), name="adverts-detail"),
    path("collect/", FetchAdsView.as_view(), name="collect-data"),
]