from .base_views import BaseModelViewSet
from ..models import ClassContentModel
from ..serializers import ClassContentModelSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
import json
from django.core.files.storage import default_storage

class ClassContentModelViewSet(BaseModelViewSet):
    queryset = ClassContentModel.objects.all()
    serializer_class = ClassContentModelSerializer
    model_name = 'contenido de clase'
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
            print("\n=== INICIO DE CREACIÓN DE CONTENIDO ===")
            print("Datos recibidos en request.data:", request.data)
            print("Archivos recibidos en request.FILES:", request.FILES)

            # Validar el content_details si está presente
            if 'content_details' in request.data:
                print("Validando content_details...")
                try:
                    if isinstance(request.data['content_details'], str):
                        content_details = json.loads(request.data['content_details'])
                        print("content_details parseado:", content_details)
                except json.JSONDecodeError as e:
                    print("Error al parsear content_details:", str(e))
                    return Response({
                        'status': 'error',
                        'message': 'Error en la validación de datos',
                        'campos_con_error': {
                            'content_details': ['El valor debe ser un JSON válido']
                        },
                        'tipo_error': 'validación'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Procesar los archivos multimedia
            if request.FILES:
                print("\nProcesando archivos multimedia...")
                multimedia_data = []
                
                # Procesar imagen de portada
                if 'cover' in request.FILES:
                    print("Procesando imagen de portada...")
                    cover_file = request.FILES['cover']
                    instance = ClassContentModel()
                    cover_info = instance.save_multimedia_file(cover_file, 'image')
                    print("Información de portada guardada:", cover_info)
                    multimedia_data.append({
                        'media_type': 'image',
                        'file_info': cover_info
                    })

                # Procesar audio
                if 'audio' in request.FILES:
                    print("Procesando archivo de audio...")
                    audio_file = request.FILES['audio']
                    instance = ClassContentModel()
                    audio_info = instance.save_multimedia_file(audio_file, 'audio')
                    print("Información de audio guardada:", audio_info)
                    multimedia_data.append({
                        'media_type': 'audio',
                        'file_info': audio_info
                    })

                if multimedia_data:
                    print("Datos multimedia procesados:", multimedia_data)
                    request.data['multimedia'] = multimedia_data

            print("\nCreando contenido usando el método de la clase padre...")
            response = super().create(request, *args, **kwargs)
            print("Respuesta de creación:", response.data)

            return Response({
                'status': 'success',
                'message': 'Contenido de clase creado exitosamente',
                'data': response.data
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            print("Error de validación:", str(e))
            return Response({
                'status': 'error',
                'message': 'Error de validación',
                'campos_con_error': str(e),
                'tipo_error': 'validación'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            print("Error inesperado:", str(e))
            print("Traceback completo:", traceback.format_exc())
            return Response({
                'status': 'error',
                'message': 'Error al crear el contenido de clase',
                'detalle_error': str(e),
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Actualizar el contenido
            response = super().update(request, *args, **kwargs)
            
            return Response({
                'status': 'success',
                'message': 'Contenido de clase actualizado exitosamente',
                'data': response.data
            })
            
        except ValidationError as e:
            return Response({
                'status': 'error',
                'message': 'Error de validación',
                'detalle_error': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al actualizar el contenido de clase',
                'detalle_error': str(e),
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
