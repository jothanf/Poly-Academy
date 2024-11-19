"""
URL configuration for pmback project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api

# Inicializa el router
router = DefaultRouter()

# Registra los viewsets
router.register(r'courses', views.CourseView, 'courses')
router.register(r'lessons', api.LessonModelViewSet)
router.register(r'layouts', api.LayoutModelViewSet)
router.register(r'multiplechoice', api.TrueOrFalseModelViewSet)
router.register(r'orderingtasks', api.OrderingTaskModelViewSet)
router.register(r'categoriestasks', api.CategoriesTaskModelViewSet)
router.register(r'fillinthegaps', api.FillInTheGapsTaskModelViewSet)


urlpatterns = [
    path('', views.home, name='home'),
    path('api/', include(router.urls)),
    path('crear_curso/', views.crear_curso, name='crear_curso'),
    path('crear_leccion/', views.crear_leccion, name='crear_leccion'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/download/', views.download_scorm, name='download_scorm'),

]
