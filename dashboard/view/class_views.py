from rest_framework import generics, status
from rest_framework.response import Response
from ..models import ClassModel
from ..serializers import (
    ClassModelSerializer, 
)
from .base_views import BaseModelViewSet
import logging

logger = logging.getLogger(__name__)

class ClassModelViewSet(BaseModelViewSet):
    queryset = ClassModel.objects.all()
    serializer_class = ClassModelSerializer
    model_name = 'clase'

    def get_queryset(self):
        """Filtra las clases por el course_id proporcionado en la URL o query params"""
        queryset = super().get_queryset()
        
        # Obtener course_id de los query params
        course_id = self.request.query_params.get('course_id')
        
        # Aplicar el filtro si hay course_id
        if course_id:
            # Usamos course_id porque es el nombre del campo en la base de datos
            queryset = queryset.filter(course_id=course_id)
            print(f"Filtrando clases para el curso {course_id}")  # Para debugging
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'status': 'success',
            'message': 'Lista de clases obtenida exitosamente',
            'data': serializer.data,
            'total': queryset.count()  # Agregamos el total para verificación
        })

    def create(self, request, *args, **kwargs):
        """Asegura que la clase se cree asociada al curso correcto"""
        course_id = self.kwargs.get('course_id')
        if course_id:
            request.data['course_id'] = course_id
        return super().create(request, *args, **kwargs)

class ClassListView(generics.ListAPIView):
    serializer_class = ClassModelSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return ClassModel.objects.filter(course_id=course_id)


class ClassDeleteView(generics.GenericAPIView):
    serializer_class = ClassModelSerializer

    def delete(self, request, pk, format=None):
        try:
            class_instance = ClassModel.objects.get(pk=pk)
            class_instance.delete()
            return Response({
                'status': 'success',
                'message': 'Clase eliminada exitosamente',
                'data': {
                    'id': class_instance.id,
                    'class_name': class_instance.class_name,
                }
            }, status=status.HTTP_200_OK)
        except ClassModel.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Clase no encontrada',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al eliminar la clase',
                'detalle_error': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

