from rest_framework import viewsets
from ..models import TeacherModel
from ..serializers import TeacherModelSerializer
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsTeacher
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
  
class TeacherViewSet(viewsets.ModelViewSet):
    queryset = TeacherModel.objects.all()
    serializer_class = TeacherModelSerializer
    
    def get_permissions(self):
        """
        Allow creation without authentication, require IsTeacher for other actions
        """
        if self.action == 'create':
            return []  # No permissions required for create action
        return [IsAuthenticated(), IsTeacher()]  # Both authentication and IsTeacher for other actions

    def get_queryset(self):
        queryset = TeacherModel.objects.all()
        return queryset.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        try:
            # Verificamos si ya existe un usuario con ese email
            email = request.data.get('email')
            if User.objects.filter(email=email).exists():
                return Response({
                    'status': 'error',
                    'message': 'Ya existe un usuario con este correo electrónico'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Manejamos los datos del formulario y la imagen
            data = request.data.dict() if hasattr(request.data, 'dict') else request.data
            
            # Verificamos el código de acceso
            access_code = data.get('access_code')
            if access_code != 'MyPolyAdmins0000':
                return Response({
                    'status': 'error',
                    'message': 'Código de acceso inválido'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Removemos el código de acceso de los datos antes de la serialización
            data.pop('access_code', None)

            # Aseguramos que el username sea igual al email si no se proporciona
            if 'username' not in data:
                data['username'] = data.get('email')  # Asignar el email como username

            # Si hay una imagen en la solicitud, la agregamos a los datos
            if 'profile_picture' in request.FILES:
                data['profile_picture'] = request.FILES['profile_picture']

            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                teacher = serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Profesor creado exitosamente',
                    'data': {
                        'id': teacher.id,
                        'username': teacher.user.email,
                        'email': teacher.user.email,
                        'profile_picture': teacher.profile_picture.url if teacher.profile_picture else None
                    }
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Error de validación',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                teacher = serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Profesor actualizado exitosamente',
                    'data': {
                        'id': teacher.id,
                        'username': teacher.user.email,
                        'email': teacher.user.email,
                        'profile_picture': teacher.profile_picture.url if teacher.profile_picture else None
                    }
                })
            return Response({
                'status': 'error',
                'message': 'Error de validación',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user = instance.user
            # Primero eliminamos el TeacherModel
            instance.delete()
            # Luego eliminamos el usuario asociado
            if user:
                user.delete()
            return Response({
                'status': 'success',
                'message': 'Profesor eliminado exitosamente'
            }, status=status.HTTP_200_OK)
        except TeacherModel.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Profesor no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al eliminar el profesor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

