from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string
from ..serializers import (
    ChangePasswordSerializer, 
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from ..models import PasswordResetCode
from ..view.email_views import send_reset_code_email
import logging

logger = logging.getLogger(__name__)

def generate_reset_code():
    """Genera un código aleatorio de 6 dígitos"""
    return ''.join(random.choices(string.digits, k=6))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if user.check_password(serializer.validated_data['old_password']):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                'status': 'success',
                'message': 'Contraseña actualizada exitosamente'
            })
        return Response({
            'status': 'error',
            'message': 'La contraseña actual es incorrecta'
        }, status=status.HTTP_400_BAD_REQUEST)
    return Response({
        'status': 'error',
        'message': 'Error de validación',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            code = generate_reset_code()
            expiry = timezone.now() + timedelta(hours=1)
            
            # Guardar o actualizar el código de recuperación
            PasswordResetCode.objects.update_or_create(
                user=user,
                defaults={
                    'code': code,
                    'expiry': expiry
                }
            )
            
            # Enviar el correo con el código
            if send_reset_code_email(email, code):
                return Response({
                    'status': 'success',
                    'message': 'Se ha enviado un código de recuperación a tu correo'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Error al enviar el correo'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except User.DoesNotExist:
            # Por seguridad, no revelamos si el email existe o no
            return Response({
                'status': 'success',
                'message': 'Si el correo existe en nuestra base de datos, recibirás un código de recuperación'
            })
            
    return Response({
        'status': 'error',
        'message': 'Error de validación',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.get(email=email)
            reset_code = PasswordResetCode.objects.get(
                user=user,
                code=code,
                expiry__gt=timezone.now(),
                used=False
            )
            
            # Actualizar la contraseña
            user.set_password(new_password)
            user.save()
            
            # Marcar el código como usado
            reset_code.used = True
            reset_code.save()
            
            return Response({
                'status': 'success',
                'message': 'Contraseña actualizada exitosamente'
            })
            
        except (User.DoesNotExist, PasswordResetCode.DoesNotExist):
            return Response({
                'status': 'error',
                'message': 'Código inválido o expirado'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    return Response({
        'status': 'error',
        'message': 'Error de validación',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST) 