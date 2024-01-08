from django.urls import URLPattern, path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("filter_year/<int:id>", views.filter_year, name="filter_year"),
    path("filter_author/<str:str>", views.filter_author, name="filter_author"),
]