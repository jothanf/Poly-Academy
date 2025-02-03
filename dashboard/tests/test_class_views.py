from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from ..models import ClassModel, CourseModel
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import json
from django.db import transaction

class ClassViewTest(APITestCase):
    @transaction.atomic
    def setUp(self):
        print("\nConfigurando test de ClassViewTest")
        self.client = APIClient()
        
        # Crear usuario y autenticar
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@test.com'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.course = CourseModel.objects.create(
            course_name="Test Course",
            description="Test Description"
        )
        print(f"Curso creado con ID: {self.course.id}")
        
        self.class_data = {
            'class_name': 'Test Class',
            'description': 'Test Description',
            'course_id': self.course.id,
            'bullet_points': ['punto 1', 'punto 2']
        }
        print("Configuración completada")

    @transaction.atomic
    def test_create_class(self):
        response = self.client.post(
            reverse('classes-list'),
            {
                'class_name': 'Clase de Prueba API',
                'description': 'Descripción de la clase de prueba',
                'course_id': self.course.id,  # Asegurarse de usar course_id
                'bullet_points': json.dumps(['punto 1', 'punto 2', 'punto 3'])
            },
            format='json'
        )
        print("Response data:", response.data)  # Debug
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ClassModel.objects.count(), 1)
        self.assertEqual(ClassModel.objects.get().class_name, 'Clase de Prueba API')

    @transaction.atomic
    def test_get_class_list(self):
        print("Iniciando test_get_class_list")  # Debug
        
        # Asegurarse de que no hay clases existentes
        ClassModel.objects.all().delete()
        print(f"Número de clases después de limpiar: {ClassModel.objects.count()}")  # Debug
        
        response = self.client.get(reverse('classes-list'))
        print(f"Response data: {response.data}")  # Debug
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar la estructura correcta de la respuesta
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 0)  # Verificar que no hay clases en data
        self.assertEqual(response.data['total'], 0)  # Verificar el total

    def test_get_class_detail(self):
        class_instance = ClassModel.objects.create(**self.class_data)
        response = self.client.get(
            reverse('classes-detail', kwargs={'pk': class_instance.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['class_name'], class_instance.class_name)

    def test_update_class(self):
        class_instance = ClassModel.objects.create(
            class_name='Clase Original',
            description='Descripción original',
            course=self.course
        )
        updated_data = {
            'class_name': 'Clase Actualizada',
            'description': 'Nueva descripción',
            'course_id': self.course.id,  # Asegurarse de usar course_id
            'bullet_points': ['punto actualizado 1', 'punto actualizado 2']
        }
        
        response = self.client.put(
            reverse('classes-detail', kwargs={'pk': class_instance.pk}),
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        class_instance.refresh_from_db()
        self.assertEqual(class_instance.class_name, 'Clase Actualizada')

    def test_delete_class(self):
        class_instance = ClassModel.objects.create(**self.class_data)
        response = self.client.delete(
            reverse('classes-detail', kwargs={'pk': class_instance.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ClassModel.objects.count(), 0) 