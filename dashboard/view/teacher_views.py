from rest_framework import viewsets
from ..models import TeacherModel
from ..serializers import TeacherModelSerializer
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsTeacher
from rest_framework import status
from rest_framework.response import Response
  
class TeacherViewSet(viewsets.ModelViewSet):
    queryset = TeacherModel.objects.all()
    serializer_class = TeacherModelSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return []  # Sin permisos para crear
        return [IsAuthenticated(), IsTeacher()]  # Permisos normales para otras acciones

    def get_queryset(self):
        queryset = TeacherModel.objects.all()
        return queryset.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        try:
            # Manejamos los datos del formulario y la imagen
            data = request.data.dict() if hasattr(request.data, 'dict') else request.data
            
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
                        'username': teacher.user.username,
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
                        'username': teacher.user.username,
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

