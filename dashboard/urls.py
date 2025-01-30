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
from .view.sessions_views import StudentLoginRecordView, UnifiedLogoutView
from .view.class_views import  ClassModelViewSet, ClassDeleteView
from .view.course_views import course_list, CourseView
from .view.ai_views import AskOpenAIView
from .view.scenario_views import ScenarioModelViewSet
from .view.student_views import StudentViewSet, create_student, StudentNoteViewSet, VocabularyEntryViewSet, StudentCoursesView, StudentListView
from .view.class_content_views import ClassContentModelViewSet
from .view.teacher_views import TeacherViewSet
from .view.ai_views import text_to_speech, AskOpenAIView, translate_message, img_gen, transcribe_audio
from .view.search_views import SearchView
from .view.sessions_views import unified_login

router = DefaultRouter()

# Registra los viewsets
router.register(r'courses', CourseView, 'courses')
router.register(r'classes', ClassModelViewSet, basename='classes')
router.register(r'scenarios', ScenarioModelViewSet, 'scenarios')
router.register(r'class-notes', StudentNoteViewSet, 'class-notes')
router.register(r'vocabulary', VocabularyEntryViewSet, 'vocabulary')
router.register(r'teachers', TeacherViewSet, 'teachers')

urlpatterns = [
    path('api/', include(router.urls)),
    path('courses/', course_list, name='course_list'),
    path('api/courses/<int:course_id>/classes/', ClassModelViewSet.as_view({'get': 'list','post': 'create'}), name='course-classes-list'),
    path('api/classes/delete/<int:pk>/', ClassDeleteView.as_view(), name='class-delete'),
    path('api/class-contents/', ClassContentModelViewSet.as_view({'get': 'list','post': 'create'}), name='class-contents-list'),
    path('api/class-contents/<int:pk>/',ClassContentModelViewSet.as_view({'get': 'retrieve', 'put': 'update','patch': 'partial_update', 'delete': 'destroy'}), name='class-contents-detail'),
    path('api/classes/', ClassModelViewSet.as_view({'get': 'list', 'post': 'create'}), name='class-list'),
    path('api/ask-openai/', AskOpenAIView.as_view(), name='ask-openai'),
    path('api/audio-transcription/', transcribe_audio, name='audio-transcription'),
    path('api/img_gen/', img_gen, name='img_gen'),
    path('api/students/', StudentViewSet.as_view(), name='student-list'),
    path('api/students/create/', create_student, name='student-create'),
    path('api/students/<int:student_id>/courses/', StudentCoursesView.as_view(), name='student-courses'),
    path('api/text-to-speech/', text_to_speech, name='text-to-speech'),
    path('api/student-login-record/', StudentLoginRecordView.as_view(), name='student-login-record'),
    path('api/search/', SearchView.as_view(), name='search'),
    path('api/login/', unified_login, name='unified-login'),
    path('api/logout/', UnifiedLogoutView.as_view(), name='unified-logout'),
    path('api/teachers/', TeacherViewSet.as_view({'get': 'list', 'post': 'create'}), name='teachers-list'),
    path('api/translate-message/', translate_message, name='translate-message'),
    path('api/students/list/', StudentListView.as_view(), name='students-list'),
]
