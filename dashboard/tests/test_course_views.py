from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from dashboard.models import CourseModel, ClassModel
from .factories import CourseFactory
import json
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class CourseViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.course_list_url = reverse('courses-list')
        self.course_data = {
            'course_name': 'Curso de Prueba API',
            'description': 'Descripción del curso de prueba',
            'category': 'Test API',
            'level': 'Principiante',
            'bullet_points': ['punto 1', 'punto 2', 'punto 3']
        }
        
        # Crear un usuario y obtener el token JWT
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@test.com'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_create_course(self):
        response = self.client.post(
            self.course_list_url,
            self.course_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CourseModel.objects.count(), 1)
        self.assertEqual(CourseModel.objects.get().course_name, 'Curso de Prueba API')

    def test_get_course_list(self):
        CourseFactory.create_batch(3)
        response = self.client.get(self.course_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_get_course_detail(self):
        course = CourseFactory()
        response = self.client.get(
            reverse('courses-detail', kwargs={'pk': course.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course_name'], course.course_name)

    def test_update_course(self):
        course = CourseFactory()
        updated_data = {
            'course_name': 'Curso Actualizado',
            'description': 'Nueva descripción',
            'bullet_points': ['punto actualizado 1', 'punto actualizado 2'],
            'category': course.category,
            'level': course.level
        }
        
        response = self.client.put(
            reverse('courses-detail', kwargs={'pk': course.pk}),
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.course_name, 'Curso Actualizado')

    def test_delete_course(self):
        course = CourseFactory()
        response = self.client.delete(
            reverse('courses-detail', kwargs={'pk': course.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CourseModel.objects.count(), 0)
