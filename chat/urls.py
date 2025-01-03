from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Inicializa el router

urlpatterns = [
    path('', views.select_scenario, name='select_scenario'),
    path('chat/<int:scenario_id>/', views.chat_room, name='chat_room'),
    path('chat-ai/', views.chat_ai, name='chat_ai'),
]