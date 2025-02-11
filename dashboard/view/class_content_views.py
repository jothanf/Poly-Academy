from .base_views import BaseModelViewSet
from ..models import ClassContentModel
from ..serializers import ClassContentModelSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid
from rest_framework import viewsets

class ClassContentModelViewSet(viewsets.ModelViewSet):
    queryset = ClassContentModel.objects.all()
    serializer_class = ClassContentModelSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        """Permite filtrar por class_id si se proporciona en la URL"""
        queryset = ClassContentModel.objects.all()
        class_id = self.request.query_params.get('class_id', None)
        if class_id is not None:
            queryset = queryset.filter(class_id=class_id)
        return queryset.order_by('order')

    def create(self, request, *args, **kwargs):
        try:
            print("=== INICIO DE CREACIÓN DE CONTENIDO ===")
            data = request.data.copy()
            
            # Manejar galería de imágenes
            if data.get('content_type') == 'gallery':
                gallery_images = []
                content_details = json.loads(data.get('content_details', '{}'))
                
                # Procesar cada imagen en la solicitud
                image_files = request.FILES.getlist('images[]')
                for index, image_file in enumerate(image_files):
                    # Guardar la imagen
                    file_path = f'gallery_images/{uuid.uuid4()}{os.path.splitext(image_file.name)[1]}'
                    saved_path = default_storage.save(file_path, image_file)
                    
                    # Crear información de la imagen
                    image_info = {
                        'title': content_details['images'][index].get('title', ''),
                        'description': content_details['images'][index].get('description', ''),
                        'image_path': saved_path,
                        'image_url': default_storage.url(saved_path)
                    }
                    gallery_images.append(image_info)
                
                # Actualizar content_details con las rutas de las imágenes
                data['content_details'] = json.dumps({'images': gallery_images})
            
            # Procesar otros tipos de contenido normalmente
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                instance = serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Contenido creado exitosamente',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Error de validación',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error al crear el contenido: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Contenido actualizado exitosamente',
                    'data': serializer.data
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Error de validación',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al actualizar el contenido: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        try:
            response = super().partial_update(request, *args, **kwargs)
            return Response({
                'status': 'success',
                'message': 'Contenido de clase actualizado parcialmente con éxito',
                'data': response.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al actualizar parcialmente el contenido de clase',
                'detalle_error': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance_id = instance.id
            
            # Eliminar archivos multimedia asociados si existen
            if instance.multimedia:
                for media_item in instance.multimedia:
                    if media_item.get('file_info', {}).get('path'):
                        default_storage.delete(media_item['file_info']['path'])
            
            super().destroy(request, *args, **kwargs)
            
            return Response({
                'status': 'success',
                'message': 'Contenido de clase eliminado exitosamente',
                'data': {'id': instance_id}
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al eliminar el contenido de clase',
                'detalle_error': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                'status': 'success',
                'message': 'Lista de contenidos obtenida exitosamente',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al obtener la lista de contenidos',
                'detalle_error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
