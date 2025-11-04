from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, RegionViewSet, HotelViewSet

router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'hotels', HotelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

