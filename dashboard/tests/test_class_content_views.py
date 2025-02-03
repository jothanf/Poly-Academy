from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from ..models import ClassContentModel, ClassModel, CourseModel
import json

class ClassContentModelViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Crear primero un curso de prueba
        self.test_course = CourseModel.objects.create(
            course_name='Curso de prueba',
            description='Descripción del curso de prueba'
        )
        
        # Crear una clase de prueba
        self.test_class = ClassModel.objects.create(
            class_name='Clase de prueba',
            description='Descripción de la clase de prueba',
            course=self.test_course
        )
        
        # Actualizar content_data con los campos correctos del modelo
        self.content_data = {
            'tittle': 'Contenido de prueba',
            'instructions': 'Instrucciones de prueba',
            'content_type': 'video',
            'class_id': self.test_class.id,  # Usar el ID en lugar del objeto
            'order': 1,
            'content_details': json.dumps({
                'duration': '10:00',
                'format': 'mp4'
            })
        }
        
        # Crear un contenido de ejemplo en la base de datos
        self.test_content = ClassContentModel.objects.create(
            class_id=self.test_class,  # Usar el objeto para crear
            **{k: v for k, v in self.content_data.items() if k != 'class_id'}
        )

    def test_list_content(self):
        """Probar obtener lista de contenidos"""
        url = reverse('classcontent-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertTrue(len(response.data['data']) > 0)

    def test_create_content(self):
        """Probar crear nuevo contenido"""
        url = reverse('classcontent-list')
        new_content = self.content_data.copy()
        new_content['tittle'] = 'Nuevo contenido'
        
        # Asegurarse de que content_details sea un objeto JSON válido y no una cadena
        new_content['content_details'] = {
            'duration': '10:00',
            'format': 'mp4'
        }
        
        response = self.client.post(url, new_content, format='json')
        
        print("Response data:", response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'success')
        
        # Verificar si hay error en la respuesta
        if 'error' in response.data['data']['status']:
            print("Error de validación:", response.data['data']['campos_con_error'])
            self.fail("La creación del contenido falló en la validación")
        
        # Corregir la navegación de la estructura de datos
        self.assertEqual(response.data['data']['data']['data']['tittle'], 'Nuevo contenido')

    def test_create_content_with_invalid_json(self):
        """Probar crear contenido con JSON inválido"""
        url = reverse('classcontent-list')
        invalid_data = self.content_data.copy()
        invalid_data['content_details'] = '{invalid json'
        
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')

    def test_update_content(self):
        """Probar actualizar contenido existente"""
        url = reverse('classcontent-detail', kwargs={'pk': self.test_content.id})
        updated_data = {
            'tittle': 'Contenido actualizado',
            'instructions': 'Nuevas instrucciones'
        }
        
        response = self.client.patch(url, updated_data, format='json')
        
        print("Update response data:", response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        # Navegar por la estructura anidada correcta
        content_data = response.data['data']['data']['data']['data']
        self.assertEqual(content_data['tittle'], 'Contenido actualizado')

    def test_delete_content(self):
        """Probar eliminar contenido"""
        url = reverse('classcontent-detail', kwargs={'pk': self.test_content.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        
        # Verificar que el contenido fue eliminado
        with self.assertRaises(ClassContentModel.DoesNotExist):
            ClassContentModel.objects.get(id=self.test_content.id)

    def test_filter_by_class_id(self):
        """Probar filtrado por class_id"""
        url = reverse('classcontent-list')
        response = self.client.get(f"{url}?class_id={self.test_class.id}")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertTrue(all(
            content['class_id'] == self.test_class.id 
            for content in response.data['data']
        ))
