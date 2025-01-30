from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from ..serializers import (
    LoginSerializer, 
    LoginResponseSerializer,
    UnifiedLogoutResponseSerializer,
    ErrorResponseSerializer
)
from rest_framework_simplejwt.exceptions import TokenError
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

@extend_schema(
    request=LoginSerializer,
    responses={200: LoginResponseSerializer},
    description="Inicio de sesión unificado para estudiantes y profesores"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def unified_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'status': 'error',
            'message': 'Email y contraseña son requeridos',
            'details': {
                'email': 'Este campo es requerido' if not email else None,
                'password': 'Este campo es requerido' if not password else None
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        
        if not user.check_password(password):
            return Response({
                'status': 'error',
                'message': 'Contraseña incorrecta',
                'details': {'password': 'La contraseña proporcionada no es válida'}
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        is_student = hasattr(user, 'studentmodel') and user.studentmodel is not None
        is_teacher = hasattr(user, 'teachermodel') and user.teachermodel is not None
        
        if not (is_student or is_teacher):
            return Response({
                'status': 'error',
                'message': 'Usuario no tiene un rol asignado',
                'details': 'El usuario no está registrado como estudiante ni como profesor'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if is_student and is_teacher:
            return Response({
                'status': 'error',
                'message': 'Usuario con múltiples roles',
                'details': 'El usuario está registrado como estudiante y profesor simultáneamente'
            }, status=status.HTTP_409_CONFLICT)
        
        user_type = 'student' if is_student else 'teacher'
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'status': 'success',
            'message': f'Inicio de sesión exitoso como {user_type}',
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user_type': user_type,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
            
    except User.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Usuario no encontrado',
            'details': f'No existe un usuario registrado con el email: {email}'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UnifiedLogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UnifiedLogoutResponseSerializer

    def post(self, request):
        try:
            # Obtener el refresh token
            refresh_token = request.data.get('refresh')
            
            # Validar que se proporcionó el token
            if not refresh_token:
                return Response({
                    'status': 'error',
                    'message': 'El token de refresco es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Intentar hacer blacklist del token
            RefreshToken(refresh_token).blacklist()

            return Response({
                'status': 'success',
                'message': 'Sesión cerrada exitosamente'
            }, status=status.HTTP_200_OK)

        except TokenError:
            # Error específico para tokens inválidos
            return Response({
                'status': 'error',
                'message': 'Token de refresco inválido'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Cualquier otro error
            print(f"Error en logout: {str(e)}")  # Para debug
            return Response({
                'status': 'error',
                'message': 'Error al cerrar sesión'
            }, status=status.HTTP_400_BAD_REQUEST) 