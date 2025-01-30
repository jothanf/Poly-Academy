from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class UnifiedLogoutTests(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        # Obtener tokens para el usuario
        self.refresh = RefreshToken.for_user(self.user)
        self.access = self.refresh.access_token
        
    def test_successful_logout(self):
        """Prueba un logout exitoso con un token válido"""
        # Autenticar el cliente
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(self.access)}')
        
        response = self.client.post(
            reverse('unified-logout'),
            {'refresh': str(self.refresh)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Sesión cerrada exitosamente')
        
    def test_logout_without_refresh_token(self):
        """Prueba un intento de logout sin proporcionar refresh token"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(self.access)}')
        
        response = self.client.post(
            reverse('unified-logout'),
            {},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'El token de refresco es requerido')
        
    def test_logout_with_invalid_refresh_token(self):
        """Prueba un intento de logout con un refresh token inválido"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(self.access)}')
        
        response = self.client.post(
            reverse('unified-logout'),
            {'refresh': 'invalid_token'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertTrue('Token de refresco inválido' in response.data['message'])
        
    def test_logout_without_authentication(self):
        """Prueba un intento de logout sin autenticación"""
        response = self.client.post(
            reverse('unified-logout'),
            {'refresh': str(self.refresh)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
