from django.urls import path
from . import views

urlpatterns = [
    path('reporters/', views.reporters_api, name='reporters_api'),
    path('issues/', views.issues_api, name='issues_api'),
]