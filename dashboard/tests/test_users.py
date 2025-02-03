from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from dashboard.models import StudentModel, TeacherModel
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import os
from PIL import Image
import io
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken


class UserAuthenticationTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Datos de prueba para estudiante
        self.student_data = {
            'username': 'estudiante_test',
            'email': 'estudiante@test.com',
            'password': 'contraseña123',
        }
        # Datos de prueba para profesor
        self.teacher_data = {
            'username': 'profesor_test',
            'email': 'profesor@test.com',
            'password': 'contraseña123',
        }

    def test_student_registration(self):
        """Prueba el registro de un estudiante"""
        response = self.client.post(
            reverse('student-create'),
            self.student_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(StudentModel.objects.filter(user__username='estudiante_test').exists())

    def test_teacher_registration(self):
        """Prueba el registro de un profesor"""
        teacher_data = {
            'username': 'profesor_test',
            'email': 'profesor@test.com',
            'password': 'contraseña123',
            'access_code': 'MyPolyAdmins0000'
        }
        print("\nIntentando registrar profesor con datos:", teacher_data)
        response = self.client.post(
            reverse('teachers-list'),
            teacher_data,
            format='json'
        )
        print(f"Respuesta del registro de profesor: {response.data}")
        print(f"Status code: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar la creación del profesor
        teacher_exists = TeacherModel.objects.filter(user__username='profesor_test').exists()
        print(f"¿Existe el profesor?: {teacher_exists}")
        self.assertTrue(teacher_exists)

    def test_unified_login(self):
        """Prueba el inicio de sesión unificado"""
        print("\n=== Test de Login Unificado ===")
        
        # 1. Crear estudiante
        print("1. Creando estudiante...")
        student_data = {
            'username': 'estudiante_test',
            'email': 'estudiante@test.com',
            'password': 'contraseña123'
        }
        create_response = self.client.post(
            reverse('student-create'),
            student_data,
            format='json'
        )
        print(f"Respuesta creación: {create_response.data}")
        
        # 2. Verificar que el usuario se creó correctamente
        user = User.objects.filter(username='estudiante_test').first()
        print(f"Usuario creado: {user}")
        print(f"¿La contraseña es válida?: {user.check_password('contraseña123')}")
        print(f"¿Tiene perfil de estudiante?: {hasattr(user, 'studentmodel')}")
        
        # 3. Intentar login
        login_data = {
            'email': student_data['email'],
            'password': student_data['password'],
            'user_type': 'student'
        }
        print("\n3. Intentando login con datos:", login_data)
        response = self.client.post(reverse('unified-login'), login_data, format='json')
        print(f"Headers de respuesta: {response.headers}")
        print(f"Respuesta completa: {response.data}")
        print(f"Status code: {response.status_code}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)  # Verificar que se recibe el token

class UserProfileTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Crear usuario y perfil de estudiante
        self.user = User.objects.create_user(
            username='test_student',
            email='test@student.com',
            password='test123'
        )
        self.student = StudentModel.objects.create(user=self.user)
        
        # Crear una imagen de prueba válida
        # Crear una imagen en memoria
        image = Image.new('RGB', (100, 100), color = 'red')
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        
        self.image = SimpleUploadedFile(
            'test_image.jpg',
            image_io.getvalue(),
            content_type='image/jpeg'
        )

    def test_update_student_profile(self):
        """Prueba la actualización del perfil de estudiante"""
        print("\n=== Test de Actualización de Perfil ===")
        self.client.force_authenticate(user=self.user)
        
        print(f"1. Usuario autenticado: {self.user.username}")
        print(f"2. ¿Tiene perfil de estudiante?: {hasattr(self.user, 'studentmodel')}")
        
        update_data = {
            'profile_picture': self.image
        }
        
        print("3. Intentando actualizar perfil...")
        response = self.client.patch(
            reverse('student-list'),
            data=update_data,
            format='multipart'
        )
        print(f"4. Respuesta: {response.data}")
        print(f"5. Status code: {response.status_code}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que la imagen se guardó
        self.student.refresh_from_db()
        print(f"6. ¿Se guardó la imagen?: {bool(self.student.profile_picture)}")

    def tearDown(self):
        # Limpiar archivos de prueba
        if self.student.profile_picture:
            if os.path.isfile(self.student.profile_picture.path):
                os.remove(self.student.profile_picture.path)

class UserPermissionsTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Crear usuario estudiante
        self.student_user = User.objects.create_user(
            username='student',
            password='test123'
        )
        self.student = StudentModel.objects.create(user=self.student_user)
        
        # Crear usuario profesor
        self.teacher_user = User.objects.create_user(
            username='teacher',
            password='test123'
        )
        self.teacher = TeacherModel.objects.create(user=self.teacher_user)

    def test_student_permissions(self):
        """Prueba los permisos de un estudiante"""
        self.client.force_authenticate(user=self.student_user)
        
        # Asegurarse de que el usuario es un estudiante
        self.assertTrue(hasattr(self.student_user, 'studentmodel'))
        
        # Un estudiante no debería poder acceder a las vistas de profesor
        response = self.client.get(reverse('teachers-list'))
        print(f"Response data: {response.data}")  # Para debugging
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_permissions(self):
        """Prueba los permisos de un profesor"""
        self.client.force_authenticate(user=self.teacher_user)
        
        # Un profesor debería poder acceder a las vistas de profesor
        response = self.client.get(reverse('teachers-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class LogoutTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test_user',
            password='test123'
        )
        # Obtener el token de refresco al autenticar el usuario
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        self.client.force_authenticate(user=self.user)

    def test_unified_logout(self):
        """Prueba el cierre de sesión unificado"""
        response = self.client.post(
            reverse('unified-logout'),
            {'refresh': self.refresh_token},  # Incluir el token de refresco en la solicitud
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success') 