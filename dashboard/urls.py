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
from .views import LayoutDetailView, ClasDeleteView, ClassTasksView, TaskLayoutDetailView

# Inicializa el router
router = DefaultRouter()

# Registra los viewsets
router.register(r'courses', views.CourseView, 'courses')
router.register(r'classes', views.ClassModelViewSet, basename='classes')
router.register(r'layouts', api.LayoutModelViewSet)
router.register(r'multiplechoice', api.MultipleChoiceModelViewSet)
router.register(r'trueorfalse', api.TrueOrFalseModelViewSet)
router.register(r'orderingtasks', api.OrderingTaskModelViewSet)
router.register(r'categoriestasks', api.CategoriesTaskModelViewSet)
router.register(r'fillinthegaps', api.FillInTheGapsTaskModelViewSet)
router.register(r'multimediablockvideos', views.MultimediaBlockVideoViewSet, 'multimediablockvideos')
router.register(r'class-contents', views.ClassContentModelViewSet, 'class-contents')

urlpatterns = [
    path('api/', include(router.urls)),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/classes/<int:class_id>/', views.ClassDetailView.as_view(), name='class_detail'),
    path('api/courses/<int:course_id>/classes/', views.ClassModelViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='course-classes-list'),
    path('api/layouts/<int:pk>/', LayoutDetailView.as_view(), name='layout-detail'),
    path('api/clases/delete/<int:pk>/', ClasDeleteView.as_view(), name='clas-delete'),
    path('api/classes/<int:class_id>/tasks/', ClassTasksView.as_view(), name='class-tasks'),
    path('api/task_layout/<int:layout_id>/', TaskLayoutDetailView.as_view(), name='task-layout-detail'),
    path('api/class-contents/', views.ClassContentModelViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='class-contents-list'),
    path('api/class-contents/<int:pk>/', views.ClassContentModelViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='class-contents-detail'),
    path('api/classes/', views.ClassModelViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='class-list'),
]
