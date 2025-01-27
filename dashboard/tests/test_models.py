from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from dashboard.models import CourseModel, ClassModel
import os

class CourseModelTest(TestCase):
    def setUp(self):
        # Crear datos de prueba que se usarán en múltiples pruebas
        self.course_data = {
            'course_name': 'Curso de Prueba',
            'description': 'Descripción del curso de prueba',
            'category': 'Test',
            'level': 'Principiante',
            'bullet_points': ['punto 1', 'punto 2', 'punto 3']
        }

    def test_course_creation(self):
        course = CourseModel.objects.create(**self.course_data)
        self.assertEqual(course.course_name, self.course_data['course_name'])
        self.assertEqual(course.description, self.course_data['description'])

    def test_course_with_cover(self):
        # Crear un archivo de imagen temporal para pruebas
        image_content = b'fake-image-content'
        cover = SimpleUploadedFile(
            name='test_image.jpg',
            content=image_content,
            content_type='image/jpeg'
        )
        
        course_with_cover = CourseModel.objects.create(
            **self.course_data,
            cover=cover
        )
        
        self.assertTrue(course_with_cover.cover)
        self.assertTrue(os.path.exists(course_with_cover.cover.path))
        
        # Limpieza: eliminar el archivo después de la prueba
        course_with_cover.cover.delete()

    def test_course_str_method(self):
        course = CourseModel.objects.create(**self.course_data)
        self.assertEqual(str(course), course.course_name)

    def test_bullet_points_json_format(self):
        course = CourseModel.objects.create(**self.course_data)
        self.assertIsInstance(course.bullet_points, list)
        self.assertEqual(len(course.bullet_points), 3)

class ClassModelTest(TestCase):
    def setUp(self):
        # Crear datos de prueba que se usarán en múltiples pruebas
        self.course = CourseModel.objects.create(**{
            'course_name': 'Curso de Prueba',
            'description': 'Descripción del curso de prueba',
            'category': 'Test',
            'level': 'Principiante',
            'bullet_points': ['punto 1', 'punto 2', 'punto 3']
        })
        self.class_data = {
            'class_name': 'Clase de Prueba',
            'description': 'Descripción de la clase de prueba',
            'course': self.course,  # Asociar la clase al curso creado
            'bullet_points': ['punto 1', 'punto 2', 'punto 3']
        }

    def test_class_creation(self):
        class_instance = ClassModel.objects.create(**self.class_data)
        self.assertEqual(class_instance.class_name, self.class_data['class_name'])
        self.assertEqual(class_instance.description, self.class_data['description'])
        self.assertEqual(class_instance.course, self.course)

    def test_class_str_method(self):
        class_instance = ClassModel.objects.create(**self.class_data)
        self.assertEqual(str(class_instance), class_instance.class_name)

    def test_bullet_points_json_format(self):
        class_instance = ClassModel.objects.create(**self.class_data)
        self.assertIsInstance(class_instance.bullet_points, list)
        self.assertEqual(len(class_instance.bullet_points), 3)

    def test_class_with_cover(self):
        # Crear un archivo de imagen temporal para pruebas
        image_content = b'fake-image-content'
        cover = SimpleUploadedFile(
            name='test_image.jpg',
            content=image_content,
            content_type='image/jpeg'
        )
        
        class_with_cover = ClassModel.objects.create(
            **self.class_data,
            cover=cover
        )
        
        self.assertTrue(class_with_cover.cover)
        self.assertTrue(os.path.exists(class_with_cover.cover.path))
        
        # Limpieza: eliminar el archivo después de la prueba
        class_with_cover.cover.delete() 