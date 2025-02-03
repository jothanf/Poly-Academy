from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from ..models import StudentModel, StudentNoteModel, VocabularyEntryModel, ClassModel, CourseModel
from ..serializers import StudentNoteModelSerializer, VocabularyEntryModelSerializer

class NoteViewsTestCase(APITestCase):
    def setUp(self):
        # Crear usuario y estudiante para pruebas
        self.user = User.objects.create_user(
            username='estudiante_test',
            email='test@example.com',
            password='testpass123'
        )
        self.student = StudentModel.objects.create(user=self.user)
        
        # Crear curso y clase para pruebas
        self.course = CourseModel.objects.create(
            course_name="Curso Test",
            description="Descripción del curso de prueba"
        )
        self.class_model = ClassModel.objects.create(
            class_name="Clase Test",
            course=self.course
        )
        
        # Crear nota de prueba
        self.note = StudentNoteModel.objects.create(
            student=self.student,
            class_id=self.class_model,
            title="Nota de prueba",
            content="Contenido de prueba",
            note_type="general"
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_note(self):
        """Prueba la creación de una nueva nota"""
        url = reverse('class-notes-list')
        data = {
            'title': 'Nueva nota',
            'content': 'Contenido de la nueva nota',
            'note_type': 'vocabulary',
            'class_id': self.class_model.id,
            'student': self.student.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudentNoteModel.objects.count(), 2)
        self.assertEqual(response.data['data']['title'], 'Nueva nota')

    def test_list_notes(self):
        """Prueba listar todas las notas del estudiante"""
        url = reverse('class-notes-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_get_note_detail(self):
        """Prueba obtener el detalle de una nota específica"""
        url = reverse('class-notes-detail', kwargs={'pk': self.note.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], 'Nota de prueba')

    def test_update_note(self):
        """Prueba actualizar una nota existente"""
        url = reverse('class-notes-detail', kwargs={'pk': self.note.id})
        data = {
            'title': 'Nota actualizada',
            'content': 'Contenido actualizado'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], 'Nota actualizada')

    def test_delete_note(self):
        """Prueba eliminar una nota"""
        url = reverse('class-notes-detail', kwargs={'pk': self.note.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(StudentNoteModel.objects.count(), 0)

class VocabularyViewsTestCase(APITestCase):
    def setUp(self):
        # Crear usuario y estudiante para pruebas
        self.user = User.objects.create_user(
            username='estudiante_test',
            email='test@example.com',
            password='testpass123'
        )
        self.student = StudentModel.objects.create(user=self.user)
        
        # Crear curso y clase para pruebas
        self.course = CourseModel.objects.create(
            course_name="Curso Test",
            description="Descripción del curso de prueba"
        )
        self.class_model = ClassModel.objects.create(
            class_name="Clase Test",
            course=self.course
        )
        
        # Crear entrada de vocabulario de prueba
        self.vocabulary_entry = VocabularyEntryModel.objects.create(
            student=self.student,
            class_model=self.class_model,
            term="test",
            translation="prueba",
            entry_type="word"
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_vocabulary_entry(self):
        """Prueba la creación de una nueva entrada de vocabulario"""
        url = reverse('vocabulary-list')
        data = {
            'term': 'hello',
            'translation': 'hola',
            'entry_type': 'word',
            'class_model': self.class_model.id,
            'student': self.student.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(VocabularyEntryModel.objects.count(), 2)
        self.assertEqual(response.data['data']['term'], 'hello')

    def test_list_vocabulary(self):
        """Prueba listar todas las entradas de vocabulario del estudiante"""
        url = reverse('vocabulary-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_toggle_favorite(self):
        """Prueba alternar el estado de favorito de una entrada"""
        url = reverse('vocabulary-toggle-favorite', kwargs={'pk': self.vocabulary_entry.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vocabulary_entry.refresh_from_db()
        self.assertTrue(self.vocabulary_entry.is_favorite)

    def test_get_favorites(self):
        """Prueba obtener solo las entradas favoritas"""
        self.vocabulary_entry.is_favorite = True
        self.vocabulary_entry.save()
        
        url = reverse('vocabulary-favorites')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_filter_by_class(self):
        """Prueba filtrar entradas por clase"""
        url = reverse('vocabulary-by-class')
        response = self.client.get(url, {'class_id': self.class_model.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
