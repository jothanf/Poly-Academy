from django.test import TestCase
from dashboard.serializers import CourseModelSerializer
from dashboard.models import CourseModel
from .factories import CourseFactory
from dashboard.serializers import ClassModelSerializer
from dashboard.models import ClassModel
from .factories import ClassFactory

class CourseSerializerTest(TestCase):
    def setUp(self):
        self.course_data = {
            'course_name': 'Curso de Prueba',
            'description': 'Descripción del curso de prueba',
            'category': 'Test',
            'level': 'Principiante',
            'bullet_points': ['punto 1', 'punto 2', 'punto 3']
        }
        self.course = CourseFactory()
        self.serializer = CourseModelSerializer(instance=self.course)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        expected_fields = {
            'id', 
            'course_name', 
            'description', 
            'category', 
            'level', 
            'bullet_points',
            'cover',
            'created_at',
            'updated_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_course_name_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['course_name'], self.course.course_name)

    def test_serializer_validation(self):
        # Prueba con datos válidos
        serializer = CourseModelSerializer(data=self.course_data)
        self.assertTrue(serializer.is_valid())

        # Prueba con datos inválidos (sin course_name)
        invalid_data = self.course_data.copy()
        invalid_data.pop('course_name')
        serializer = CourseModelSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('course_name', serializer.errors)

    def test_serializer_creates_course(self):
        serializer = CourseModelSerializer(data=self.course_data)
        self.assertTrue(serializer.is_valid())
        course = serializer.save()
        self.assertIsInstance(course, CourseModel)
        self.assertEqual(course.course_name, self.course_data['course_name'])

    def test_serializer_updates_course(self):
        updated_data = {
            'course_name': 'Curso Actualizado',
            'description': 'Nueva descripción'
        }
        serializer = CourseModelSerializer(
            instance=self.course,
            data=updated_data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_course = serializer.save()
        self.assertEqual(updated_course.course_name, 'Curso Actualizado')

class ClassSerializerTest(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.class_data = {
            'class_name': 'Clase de Prueba',
            'description': 'Descripción de la clase de prueba',
            'course_id': self.course.id,
            'bullet_points': ['punto 1', 'punto 2', 'punto 3']
        }
        self.class_instance = ClassFactory(course=self.course)
        self.serializer = ClassModelSerializer(instance=self.class_instance)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        expected_fields = {
            'id', 
            'class_name', 
            'description', 
            'course_id',
            'bullet_points',
            'cover',
            'created_at',
            'updated_at'
        }
        print("Campos actuales:", set(data.keys()))  # Debug
        print("Campos esperados:", expected_fields)  # Debug
        self.assertEqual(set(data.keys()), expected_fields)

    def test_class_name_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['class_name'], self.class_instance.class_name)

    def test_serializer_validation(self):
        # Prueba con datos válidos
        serializer = ClassModelSerializer(data=self.class_data)
        self.assertTrue(serializer.is_valid())

        # Prueba con datos inválidos (sin class_name)
        invalid_data = self.class_data.copy()
        invalid_data.pop('class_name')
        serializer = ClassModelSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('class_name', serializer.errors)

    def test_serializer_creates_class(self):
        serializer = ClassModelSerializer(data=self.class_data)
        self.assertTrue(serializer.is_valid())
        class_instance = serializer.save()
        self.assertIsInstance(class_instance, ClassModel)
        self.assertEqual(class_instance.class_name, self.class_data['class_name'])

    def test_serializer_updates_class(self):
        updated_data = {
            'class_name': 'Clase Actualizada',
            'description': 'Nueva descripción',
            'course': self.course.id
        }
        serializer = ClassModelSerializer(
            instance=self.class_instance,
            data=updated_data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_class = serializer.save()
        self.assertEqual(updated_class.class_name, 'Clase Actualizada') 