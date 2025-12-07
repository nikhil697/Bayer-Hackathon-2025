from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload, name='upload'),
    path('compare/', views.compare, name='compare'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
