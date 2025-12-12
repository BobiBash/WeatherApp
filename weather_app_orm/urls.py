from django.urls import path
from . import views

urlpatterns = [
    path("", views.search_weather, name="search_weather"),
    path("weather/<str:city>/", views.city_weather, name="city_weather"),
    path('autocomplete/', views.autocomplete, name='autocomplete')
]