from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from dashboard.models import CourseModel
from .factories import CourseFactory
from dashboard.view.base_views import BaseModelViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.test import force_authenticate
from rest_framework import serializers

# Agregar este serializer de prueba
class TestCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModel
        fields = ['id', 'course_name', 'description', 'category', 'level']

class TestModelViewSet(BaseModelViewSet):
    queryset = CourseModel.objects.all()
    serializer_class = TestCourseSerializer
    model_name = 'Curso'
    
class BaseViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Crear usuario de prueba y autenticación
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@test.com'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Configurar el ViewSet de prueba
        self.viewset = TestModelViewSet()
        self.viewset.request = self.client.request()
        self.viewset.format_kwarg = None
        
        # Datos de prueba
        self.test_data = {
            'course_name': 'Curso de Prueba',
            'description': 'Descripción de prueba',
            'category': 'Test',
            'level': 'Principiante'
        }

    def test_create_success(self):
        request = self.client.post('/', self.test_data, format='json')
        force_authenticate(request, user=self.user)
        
        self.viewset.request = request
        self.viewset.kwargs = {}
        
        response = self.viewset.create(request)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)

    def test_create_validation_error(self):
        invalid_data = {'course_name': ''}
        request = self.client.post('/', invalid_data, format='json')
        force_authenticate(request, user=self.user)
        
        self.viewset.request = request
        self.viewset.kwargs = {}
        
        response = self.viewset.create(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('campos_con_error', response.data)

    def test_update_success(self):
        course = CourseFactory()
        updated_data = {
            'course_name': 'Curso Actualizado',
            'description': 'Nueva descripción'
        }
        request = self.client.put(f'/{course.id}/', updated_data, format='json')
        force_authenticate(request, user=self.user)
        
        self.viewset.request = request
        self.viewset.kwargs = {'pk': course.id}
        
        response = self.viewset.update(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)

    def test_partial_update_success(self):
        course = CourseFactory()
        partial_data = {'course_name': 'Nombre Parcialmente Actualizado'}
        request = self.client.patch(f'/{course.id}/', partial_data, format='json')
        force_authenticate(request, user=self.user)
        
        self.viewset.kwargs = {'pk': course.id}
        response = self.viewset.partial_update(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    def test_destroy_success(self):
        course = CourseFactory()
        request = self.client.delete(f'/{course.id}/')
        force_authenticate(request, user=self.user)
        
        self.viewset.request = request
        self.viewset.kwargs = {'pk': course.id}
        
        response = self.viewset.destroy(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)
