from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from dashboard.models import CourseModel, ClassModel
from .factories import CourseFactory
import json
from django.db import transaction

class CourseViewTest(APITestCase):
    def setUp(self):
        self.client = Client()
        self.course_list_url = reverse('courses-list')
        self.course_data = {
            'course_name': 'Curso de Prueba API',
            'description': 'Descripción del curso de prueba',
            'category': 'Test API',
            'level': 'Principiante',
            'bullet_points': json.dumps(['punto 1', 'punto 2', 'punto 3'])
        }

    def test_create_course(self):
        response = self.client.post(
            self.course_list_url,
            self.course_data,
            format='json'
        )
        print(response.data)
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
        
        # Configurar los headers correctamente
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = self.client.put(
            reverse('courses-detail', kwargs={'pk': course.pk}),
            data=json.dumps(updated_data),
            content_type='application/json',
            **headers
        )
        
        # Imprimir información de depuración
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.course_name, 'Curso Actualizado')

    def test_delete_course(self):
        course = CourseFactory()
        response = self.client.delete(
            reverse('courses-detail', kwargs={'pk': course.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CourseModel.objects.count(), 0)

class ClassViewTest(APITestCase):
    @transaction.atomic
    def setUp(self):
        print("\nConfigurando test de ClassViewTest")  # Debug
        self.client = Client()
        self.course = CourseModel.objects.create(
            course_name="Test Course",
            description="Test Description"
        )
        print(f"Curso creado con ID: {self.course.id}")  # Debug
        
        self.class_data = {
            'class_name': 'Test Class',
            'description': 'Test Description',
            'course_id': self.course.id,
            'bullet_points': ['punto 1', 'punto 2']
        }
        print("Configuración completada")  # Debug

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