from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.http import HttpResponse, JsonResponse
from .serializers import CourseModelSerializer, ClassModelSerializer, LayoutModelSerializer, MultipleChoiceModelSerializer,  TrueOrFalseModelSerializer, OrderingTaskModelSerializer, CategoriesTaskModelSerializer, FillInTheGapsTaskModelSerializer, VideoLayoutModelSerializer, TextBlockLayoutModelSerializer, MediaModelSerializer, MultimediaBlockVideoModelSerializer, ClassContentModelSerializer, ScenarioModelSerializer, FormattedTextModelSerializer, StudentModelSerializer, StudentNoteModelSerializer, VocabularyEntryModelSerializer, TeacherModelSerializer, StudentLoginRecordSerializer, AskOpenAISerializer, TranscribeAudioSerializer, LoginSerializer, SearchSerializer, TextToSpeechRequestSerializer, TextToSpeechResponseSerializer, LoginResponseSerializer, SuccessResponseSerializer, ErrorResponseSerializer, MessageResponseSerializer, GenericResponseSerializer, LogoutResponseSerializer, StudentCoursesSerializer, UnifiedLogoutResponseSerializer
from .models import CourseModel, ClassModel, LayoutModel, MultipleChoiceModel,TrueOrFalseModel, OrderingTaskModel, CategoriesTaskModel, FillInTheGapsTaskModel, VideoLayoutModel, TextBlockLayoutModel, MediaModel, MultimediaBlockVideoModel, ClassContentModel, ScenarioModel, FormattedTextModel, StudentModel, StudentNoteModel, VocabularyEntryModel, TeacherModel, StudentLoginRecord
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework import generics
import logging
from django.core.files.storage import default_storage
import json
from .IA.openAI import AIService
from rest_framework.decorators import api_view
import tempfile
import os
from .IA.imgGen import ImageGenerator
from django.views.decorators.csrf import csrf_exempt
import uuid
from rest_framework.decorators import action  # Asegúrate de que la ruta sea correcta
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from itertools import chain
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiResponse

# Configurar el logger
logger = logging.getLogger(__name__)

# Create your views here.


class BaseModelViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({
                'status': 'success',
                'message': f'{self.model_name} creado exitosamente',
                'data': response.data
            }, status=status.HTTP_201_CREATED)
        except DRFValidationError as e:
            error_details = {}
            if isinstance(e.detail, dict):
                for field, errors in e.detail.items():
                    error_details[field] = [str(error) for error in errors]
            else:
                error_details['general'] = [str(error) for error in e.detail]

            return Response({
                'status': 'error',
                'message': 'Error en la validación de datos',
                'campos_con_error': error_details,
                'tipo_error': 'validación'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al crear {self.model_name}',
                'detalle_error': str(e),
                'tipo_error': 'sistema'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, 
                data=request.data, 
                partial=kwargs.get('partial', False)
            )
            
            if serializer.is_valid():
                self.perform_update(serializer)
                return Response({
                    'status': 'success',
                    'message': 'Curso actualizado exitosamente',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Error al actualizar el curso',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al actualizar el curso: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            super().destroy(request, *args, **kwargs)
            return Response({
                'status': 'success',
                'message': f'{self.model_name} eliminado exitosamente',
                'data': {
                    'id': instance.id,
                    'course_name': instance.course_name if hasattr(instance, 'course_name') else None,
                    'class_name': instance.class_name if hasattr(instance, 'class_name') else None,
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al eliminar {self.model_name}',
                'detalle_error': str(e),
                'tipo_error': 'sistema'
            }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        try:
            response = super().partial_update(request, *args, **kwargs)
            return Response({
                'status': 'success',
                'message': f'{self.model_name} actualizado parcialmente con éxito',
                'data': response.data
            })
        except DRFValidationError as e:
            error_details = {}
            if isinstance(e.detail, dict):
                for field, errors in e.detail.items():
                    error_details[field] = [str(error) for error in errors]
            else:
                error_details['general'] = [str(error) for error in e.detail]

            return Response({
                'status': 'error',
                'message': f'Error al actualizar parcialmente {self.model_name}',
                'campos_con_error': error_details,
                'tipo_error': 'validación'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al actualizar parcialmente {self.model_name}',
                'detalle_error': str(e),
                'tipo_error': 'sistema'
            }, status=status.HTTP_400_BAD_REQUEST)

class CourseView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CourseModel.objects.all()
    serializer_class = CourseModelSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def create(self, request, *args, **kwargs):
        try:
            imagen = request.FILES.get('imagen')
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                return Response({
                    'status': 'success',
                    'message': 'Curso creado exitosamente',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Error al crear el curso',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al crear el curso: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

class LayoutModelViewSet(BaseModelViewSet):
    queryset = LayoutModel.objects.all()
    serializer_class = LayoutModelSerializer
    model_name = 'layout'

class MultipleChoiceModelViewSet(BaseModelViewSet):
    queryset = MultipleChoiceModel.objects.all()
    serializer_class = MultipleChoiceModelSerializer
    model_name = 'modelo de elección múltiple'

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({
                'status': 'success',
                'message': 'Modelo de elección múltiple creado exitosamente',
                'data': response.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al crear el modelo de elección múltiple',
                'detalle_error': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                'status': 'success',
                'message': 'Modelo de elección múltiple actualizado exitosamente',
                'data': response.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al actualizar el modelo de elección múltiple',
                'detalle_error': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

class TrueOrFalseModelViewSet(BaseModelViewSet):
    queryset = TrueOrFalseModel.objects.all()
    serializer_class = TrueOrFalseModelSerializer
    model_name = 'modelo de verdadero o falso'

class OrderingTaskModelViewSet(BaseModelViewSet):
    queryset = OrderingTaskModel.objects.all()
    serializer_class = OrderingTaskModelSerializer
    model_name = 'tarea de ordenamiento'

class CategoriesTaskModelViewSet(BaseModelViewSet):
    queryset = CategoriesTaskModel.objects.all()
    serializer_class = CategoriesTaskModelSerializer
    model_name = 'tarea de categorías'

class FillInTheGapsTaskModelViewSet(BaseModelViewSet):
    queryset = FillInTheGapsTaskModel.objects.all()
    serializer_class = FillInTheGapsTaskModelSerializer
    model_name = 'tarea de rellenar huecos'

def course_list(request):
    courses = CourseModel.objects.all().order_by('-created_at')
    return render(request, 'course_list.html', {'courses': courses})

class ClassDetailView(RetrieveAPIView):
    serializer_class = ClassModelSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return ClassModel.objects.filter(course_id=course_id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        logger.debug(f"Obteniendo detalles de la clase: {instance.class_name}")

        # Obtener todos los layouts asociados a la clase
        layouts = instance.layouts.all()  # Acceder a todos los layouts de la clase
        logger.debug(f"Número de layouts encontrados: {layouts.count()}")

        # Inicializar listas para las tareas
        multiple_choice_tasks = []
        true_or_false_tasks = []
        ordering_tasks = []
        categories_tasks = []
        fill_in_the_gaps_tasks = []

        # Iterar sobre cada layout y obtener las tareas
        for layout in layouts:
            logger.debug(f"Procesando layout: {layout.title}")
            multiple_choice_tasks.extend(layout.multiplechoicemodel_set.all())
            true_or_false_tasks.extend(layout.trueorfalsemodel_set.all())
            ordering_tasks.extend(layout.orderingtaskmodel_set.all())
            categories_tasks.extend(layout.categoriestaskmodel_set.all())
            fill_in_the_gaps_tasks.extend(layout.fillinthegapstaskmodel_set.all())

        logger.debug(f"Tareas de opción múltiple encontradas: {len(multiple_choice_tasks)}")
        logger.debug(f"Tareas de verdadero/falso encontradas: {len(true_or_false_tasks)}")
        logger.debug(f"Tareas de ordenamiento encontradas: {len(ordering_tasks)}")
        logger.debug(f"Tareas de categorías encontradas: {len(categories_tasks)}")
        logger.debug(f"Tareas de llenar espacios encontradas: {len(fill_in_the_gaps_tasks)}")

        return Response({
            'class': serializer.data,
            'multiple_choice_tasks': MultipleChoiceModelSerializer(multiple_choice_tasks, many=True).data,
            'true_or_false_tasks': TrueOrFalseModelSerializer(true_or_false_tasks, many=True).data,
            'ordering_tasks': OrderingTaskModelSerializer(ordering_tasks, many=True).data,
            'categories_tasks': CategoriesTaskModelSerializer(categories_tasks, many=True).data,
            'fill_in_the_gaps_tasks': FillInTheGapsTaskModelSerializer(fill_in_the_gaps_tasks, many=True).data,
        })

class ClassListView(generics.ListAPIView):
    serializer_class = ClassModelSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return ClassModel.objects.filter(course_id=course_id)

class LayoutDetailView(RetrieveAPIView):
    serializer_class = LayoutModelSerializer

    def get_queryset(self):
        return LayoutModel.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Obtener todas las tareas asociadas al layout
        multiple_choice_tasks = instance.questions.all()  # Tareas de opción múltiple
        true_or_false_tasks = instance.true_or_false_tasks.all()  # Tareas de verdadero o falso
        ordering_tasks = instance.ordering_tasks.all()  # Tareas de ordenamiento
        categories_tasks = instance.categories_tasks.all()  # Tareas de categorías
        fill_in_the_gaps_tasks = instance.fill_in_the_gaps_tasks.all()  # Tareas de llenar espacios

        return Response({
            'layout': serializer.data,
            'multiple_choice_tasks': MultipleChoiceModelSerializer(multiple_choice_tasks, many=True).data,
            'true_or_false_tasks': TrueOrFalseModelSerializer(true_or_false_tasks, many=True).data,
            'ordering_tasks': OrderingTaskModelSerializer(ordering_tasks, many=True).data,
            'categories_tasks': CategoriesTaskModelSerializer(categories_tasks, many=True).data,
            'fill_in_the_gaps_tasks': FillInTheGapsTaskModelSerializer(fill_in_the_gaps_tasks, many=True).data,
        })

class ClasDeleteView(generics.GenericAPIView):
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

class ClassTasksView(generics.GenericAPIView):
    serializer_class = ClassModelSerializer

    def get(self, request, class_id, format=None):
        try:
            class_instance = ClassModel.objects.get(id=class_id)
            layouts = class_instance.layouts.all()
            videos = class_instance.videos.all()
            text_blocks = class_instance.text_blocks.all()

            # Inicializar listas para las tareas y contenido
            multiple_choice_tasks = []
            true_or_false_tasks = []
            ordering_tasks = []
            categories_tasks = []
            fill_in_the_gaps_tasks = []
            media_items = set()  # Usamos un set para evitar duplicados

            # Serializar los layouts
            layouts_data = []
            for layout in layouts:
                layout_data = LayoutModelSerializer(layout).data
                layout_data.update({
                    'multiple_choice': MultipleChoiceModelSerializer(layout.questions.all(), many=True).data,
                    'true_or_false': TrueOrFalseModelSerializer(layout.true_or_false_tasks.all(), many=True).data,
                    'ordering': OrderingTaskModelSerializer(layout.ordering_tasks.all(), many=True).data,
                    'categories': CategoriesTaskModelSerializer(layout.categories_tasks.all(), many=True).data,
                    'fill_in_the_gaps': FillInTheGapsTaskModelSerializer(layout.fill_in_the_gaps_tasks.all(), many=True).data,
                })
                layouts_data.append(layout_data)

                # Recopilar multimedia de las tareas
                for task in layout.questions.all():
                    media_items.update(task.media.all())
                for task in layout.true_or_false_tasks.all():
                    media_items.update(task.media.all())
                for task in layout.ordering_tasks.all():
                    media_items.update(task.media.all())
                for task in layout.categories_tasks.all():
                    media_items.update(task.media.all())
                for task in layout.fill_in_the_gaps_tasks.all():
                    media_items.update(task.media.all())

            return Response({
                'status': 'success',
                'class_id': class_instance.id,
                'class_name': class_instance.class_name,
                'cover': class_instance.cover.url if class_instance.cover else None,
                'description': class_instance.description,
                'bullet_points': class_instance.bullet_points,
                'task_layouts': layouts_data,
                'video_layouts': VideoLayoutModelSerializer(videos, many=True).data,  # Videos separados
                'text_blocks_layouts': TextBlockLayoutModelSerializer(text_blocks, many=True).data,  # Textos separados
                'media': MediaModelSerializer(list(media_items), many=True).data
            }, status=status.HTTP_200_OK)
        except ClassModel.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Clase no encontrada',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al obtener las tareas',
                'detalle_error': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

class TaskLayoutDetailView(generics.GenericAPIView):
    serializer_class = LayoutModelSerializer

    def get(self, request, layout_id, format=None):
        try:
            layout_instance = LayoutModel.objects.get(id=layout_id)
            multiple_choice_tasks = layout_instance.questions.all()
            true_or_false_tasks = layout_instance.true_or_false_tasks.all()
            ordering_tasks = layout_instance.ordering_tasks.all()
            categories_tasks = layout_instance.categories_tasks.all()
            fill_in_the_gaps_tasks = layout_instance.fill_in_the_gaps_tasks.all()

            # Obtener multimedia asociada a las tareas
            media_items = set()
            for task in multiple_choice_tasks:
                media_items.update(task.media.all())
            for task in true_or_false_tasks:
                media_items.update(task.media.all())
            for task in ordering_tasks:
                media_items.update(task.media.all())
            for task in categories_tasks:
                media_items.update(task.media.all())
            for task in fill_in_the_gaps_tasks:
                media_items.update(task.media.all())

            return Response({
                'status': 'success',
                'layout_id': layout_instance.id,
                'layout_title': layout_instance.title,
                'instructions': layout_instance.instructions,  # Instrucciones
                'cover': layout_instance.cover.url if layout_instance.cover else None,  # Cover
                'audio': layout_instance.audio.url if layout_instance.audio else None,  # Audio
                'audio_script': layout_instance.audio_script,  # Audio script
                'tasks': {
                    'multiple_choice': MultipleChoiceModelSerializer(multiple_choice_tasks, many=True).data,
                    'true_or_false': TrueOrFalseModelSerializer(true_or_false_tasks, many=True).data,
                    'ordering': OrderingTaskModelSerializer(ordering_tasks, many=True).data,
                    'categories': CategoriesTaskModelSerializer(categories_tasks, many=True).data,
                    'fill_in_the_gaps': FillInTheGapsTaskModelSerializer(fill_in_the_gaps_tasks, many=True).data,
                },
                'media': MediaModelSerializer(list(media_items), many=True).data
            }, status=status.HTTP_200_OK)
        except LayoutModel.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Layout no encontrado',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al obtener el layout',
                'detalle_error': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

class MultimediaBlockVideoViewSet(viewsets.ModelViewSet):
    queryset = MultimediaBlockVideoModel.objects.all()
    serializer_class = MultimediaBlockVideoModelSerializer

    # Método para listar todos los videos
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al crear el bloque multimedia de video',
                'detalle_error': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al actualizar el bloque multimedia de video',
                'detalle_error': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al eliminar el bloque multimedia de video',
                'detalle_error': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

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
            print("Datos recibidos:", request.data)  # Debug
            # Validar el content_details si está presente
            if 'content_details' in request.data:
                try:
                    if isinstance(request.data['content_details'], str):
                        json.loads(request.data['content_details'])
                except json.JSONDecodeError:
                    return Response({
                        'status': 'error',
                        'message': 'Error en la validación de datos',
                        'campos_con_error': {
                            'content_details': ['El valor debe ser un JSON válido']
                        },
                        'tipo_error': 'validación'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Procesar los archivos multimedia si están presentes
            multimedia_files = request.FILES.getlist('multimedia')
            
            # Crear el contenido usando el método de la clase padre
            response = super().create(request, *args, **kwargs)
            
            # Si llegamos aquí, la creación fue exitosa
            return Response({
                'status': 'success',
                'message': 'Contenido de clase creado exitosamente',
                'data': response.data
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({
                'status': 'error',
                'message': 'Error de validación',
                'campos_con_error': str(e),
                'tipo_error': 'validación'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            print("Error detallado:", traceback.format_exc())  # Debug
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

# Primero, crea un serializer para la vista


# Luego, modifica la vista para usar GenericAPIView y el serializer
class AskOpenAIView(generics.GenericAPIView):
    serializer_class = AskOpenAISerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            ai_service = AIService()
            question = serializer.validated_data['question']
            
            answer = ai_service.chat_with_gpt(question)
            
            return Response({
                'status': 'success',
                'answer': answer
            }, status=status.HTTP_200_OK)
            
        return Response({
            'status': 'error',
            'message': 'Error al procesar la solicitud',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    request=TranscribeAudioSerializer,
    responses={
        200: SuccessResponseSerializer,
        400: ErrorResponseSerializer
    }
)
@api_view(['POST'])
def transcribe_audio(request):
    try:
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response(
                {'error': 'No se proporcionó archivo de audio'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Guardar el archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
            for chunk in audio_file.chunks():
                temp_audio.write(chunk)
            temp_audio_path = temp_audio.name

        try:
            # Usar el servicio AI para transcribir
            ai_service = AIService()
            result = ai_service.client.audio.transcriptions.create(
                model="whisper-1",
                file=open(temp_audio_path, "rb")
            )

            # Analizar la pronunciación después de la transcripción
            pronunciation_analysis = ai_service.analyze_pronunciation(result.text)

            return Response({
                'status': 'success',
                'data': {
                    'transcription': result.text,
                    'pronunciation_analysis': pronunciation_analysis
                }
            })

        finally:
            # Limpiar el archivo temporal
            try:
                os.unlink(temp_audio_path)
            except Exception as e:
                print(f"Error al eliminar archivo temporal: {e}")

    except Exception as e:
        print(f"Error en transcribe_audio: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class ScenarioSuggestionsView(generics.GenericAPIView):
    serializer_class = ScenarioModelSerializer
    
    def post(self, request):
        try:
            ai_service = AIService()
            scenario_info = {
                'nombre': request.data.get('nombre', ''),
                'nivel': request.data.get('nivel', ''),
                'tipo': request.data.get('tipo', ''),
                'lugar': request.data.get('lugar', ''),
                'descripcion': request.data.get('descripcion', '')
            }
            
            suggestions = ai_service.generate_scenario_suggestions(scenario_info)
            
            if "error" in suggestions:
                return Response({
                    'status': 'error',
                    'message': suggestions['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'status': 'success',
                'data': suggestions
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al procesar la solicitud: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ScenarioModelViewSet(viewsets.ModelViewSet):
    queryset = ScenarioModel.objects.all()
    serializer_class = ScenarioModelSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        queryset = ScenarioModel.objects.all()
        class_id = self.request.query_params.get('class_id', None)
        if class_id is not None:
            queryset = queryset.filter(class_model_id=class_id)
        return queryset.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                scenario = serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Escenario creado exitosamente',
                    'data': serializer.data
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
                scenario = serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Escenario actualizado exitosamente',
                    'data': serializer.data
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
            instance.delete()
            return Response({
                'status': 'success',
                'message': 'Escenario eliminado exitosamente'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FormattedTextViewSet(viewsets.ModelViewSet):
    queryset = FormattedTextModel.objects.all()
    serializer_class = FormattedTextModelSerializer

    def get_queryset(self):
        queryset = FormattedTextModel.objects.all()
        class_id = self.request.query_params.get('class_id', None)
        if class_id is not None:
            queryset = queryset.filter(class_model_id=class_id)
        return queryset.order_by('-created_at')  # Ordenar por fecha de creación descendente

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Obtener el límite de la query params
        limit = request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]
            
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'message': 'Textos formateados obtenidos exitosamente',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        try:
            print("Datos recibidos:", request.data)  # Debug
            # Validaciones explícitas
            if 'class_model' not in request.data:
                return Response({
                    'status': 'error',
                    'message': 'El campo class_model es requerido',
                    'errors': {'class_model': ['Este campo es requerido']}
                }, status=status.HTTP_400_BAD_REQUEST)

            if 'content' not in request.data:
                return Response({
                    'status': 'error',
                    'message': 'El campo content es requerido',
                    'errors': {'content': ['Este campo es requerido']}
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                print("Errores de validación:", serializer.errors)
                return Response({
                    'status': 'error',
                    'message': 'Error de validación',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            self.perform_create(serializer)
            
            return Response({
                'status': 'success',
                'message': 'Texto formateado creado exitosamente',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            print("Error detallado:", traceback.format_exc())  # Debug
            return Response({
                'status': 'error',
                'message': str(e),
                'traceback': traceback.format_exc()
            }, status=500)

@csrf_exempt
def img_gen(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
          
            prompt = data.get('prompt')
            if not prompt:
                return JsonResponse({'error': 'No se proporcionó un prompt'}, status=400)
            
            generator = ImageGenerator()
            result = generator.generate_image(prompt)
            
            if result['success']:
                return JsonResponse({'url': result['url']})
            else:
                return JsonResponse({'error': result['error']}, status=500)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'img_gen.html')

@extend_schema(exclude=True)
@api_view(['GET', 'POST'])
def prueva_json(request):
    if request.method == 'GET':
        try:
            content_type = request.query_params.get('content_type')
            contents = ClassContentModel.objects.all()
            if content_type:
                contents = contents.filter(content_type=content_type)
            
            serializer = ClassContentModelSerializer(contents, many=True)
            
            if request.headers.get('Accept') == 'application/json':
                return Response({
                    'status': 'success',
                    'data': serializer.data
                })
            
            return render(request, 'prueva_json.html')
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=400)

    elif request.method == 'POST':
        try:
            data = request.data
            
            # Validar class_id
            try:
                class_instance = ClassModel.objects.get(id=data.get('class_id'))
            except ClassModel.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Clase no encontrada'
                }, status=400)

            # Crear el objeto de contenido
            content_data = {
                'class_id': class_instance.id,  # Cambiado para usar el ID en lugar del objeto
                'content_type': 'picture_matching_knowledge_check',
                'tittle': data.get('title'),
                'content_details': data.get('content_details', {})
            }

            # Crear el serializer con los datos
            serializer = ClassContentModelSerializer(data=content_data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Contenido creado exitosamente',
                    'data': serializer.data
                })
            else:
                # Devolver errores detallados de validación
                return Response({
                    'status': 'error',
                    'message': 'Error de validación',
                    'errors': serializer.errors,
                    'received_data': content_data  # Agregar datos recibidos para debugging
                }, status=400)

        except Exception as e:
            import traceback
            return Response({
                'status': 'error',
                'message': str(e),
                'traceback': traceback.format_exc()  # Agregar traceback para debugging
            }, status=500)

def save_multimedia_file(file, media_type):
    if not file:
        return None

    ext = os.path.splitext(file.name)[1]
    filename = f"content_media/{uuid.uuid4()}{ext}"
    path = default_storage.save(filename, file)
    
    return {
        'name': file.name,
        'url': default_storage.url(path),
        'path': path,
        'media_type': media_type,
        'size': file.size
    }

def prueba_classcontent(request):
    # Consultar todos los ClassContentModel donde content_type sea 'image'
    contents = ClassContentModel.objects.filter(content_type='image')
    return render(request, 'prueba_classcontent.html', {'contents': contents})

def StudentRegisterView():
    queryset = StudentModel.objects.all()
            
@extend_schema(
    request=StudentModelSerializer,
    responses={201: StudentModelSerializer}
)
@api_view(['POST'])
def create_student(request):
    """
    Vista para crear un nuevo estudiante.
    """
    serializer = StudentModelSerializer(data=request.data)
    if serializer.is_valid():
        try:
            student = serializer.save()
            return Response({
                'status': 'success',
                'message': 'Estudiante creado exitosamente',
                'data': {
                    'id': student.id,
                    'username': student.user.username,
                    'email': student.user.email
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al crear el estudiante',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    return Response({
        'status': 'error',
        'message': 'Error de validación',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
            
class StudentListView(generics.ListAPIView):
    queryset = StudentModel.objects.all()
    serializer_class = StudentModelSerializer

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })
            
class StudentViewSet(generics.ListCreateAPIView):
    queryset = StudentModel.objects.all()
    serializer_class = StudentModelSerializer

    def get(self, request, *args, **kwargs):
        students = self.get_queryset()
        serializer = self.get_serializer(students, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        })

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                student = serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Estudiante creado exitosamente',
                    'data': {
                        'id': student.id,
                        'username': student.user.username,
                        'email': student.user.email
                    }
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'status': 'error',
                    'message': 'Error al crear el estudiante',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'status': 'error',
            'message': 'Error de validación',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
            
class StudentCoursesView(generics.GenericAPIView):
    serializer_class = StudentCoursesSerializer

    def get(self, request, student_id):
        try:
            student = StudentModel.objects.get(id=student_id)
            courses = student.courses.all()
            serializer = CourseModelSerializer(courses, many=True)
            return Response({
                'status': 'success',
                'message': 'Cursos del estudiante obtenidos exitosamente',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except StudentModel.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Estudiante no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
def student_courses(request, student_id):
    student = StudentModel.objects.get(id=student_id)
    courses = student.courses.all()
    return render(request, 'student_courses.html', {'courses': courses})

class StudentNoteViewSet(viewsets.ModelViewSet):
    serializer_class = StudentNoteModelSerializer
    
    def get_queryset(self):
        """
        Filtra las notas por estudiante si se proporciona student_id en la URL
        """
        queryset = StudentNoteModel.objects.all()
        student_id = self.request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        return queryset.order_by('-updated_at')

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Nota creada exitosamente',
                    'data': serializer.data
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
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Nota actualizada exitosamente',
                    'data': serializer.data
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
            instance.delete()
            return Response({
                'status': 'success',
                'message': 'Nota eliminada exitosamente'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VocabularyEntryViewSet(viewsets.ModelViewSet):
    serializer_class = VocabularyEntryModelSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        queryset = VocabularyEntryModel.objects.all()
        student_id = self.request.query_params.get('student_id', None)
        if student_id is not None:
            queryset = queryset.filter(student_id=student_id)
        return queryset.order_by('-updated_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'message': 'Vocabulario obtenido exitosamente',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                'status': 'success',
                'message': 'Entrada de vocabulario creada exitosamente',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                'status': 'success',
                'message': 'Entrada de vocabulario actualizada exitosamente',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_proficiency(self, request, pk=None):
        try:
            entry = self.get_object()
            success_rate = float(request.data.get('success_rate', 0))
            entry.update_proficiency(success_rate)
            serializer = self.get_serializer(entry)
            return Response({
                'status': 'success',
                'message': 'Nivel de dominio actualizado exitosamente',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = TeacherModel.objects.all()
    serializer_class = TeacherModelSerializer
    parser_classes = (MultiPartParser, FormParser)  # Agregamos soporte para archivos

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


@extend_schema(
    request=TextToSpeechRequestSerializer,
    responses={
        200: TextToSpeechResponseSerializer,
        400: OpenApiResponse(
            response=TextToSpeechResponseSerializer,
            description='Error en la solicitud'
        )
    }
)
@api_view(['POST'])
def text_to_speech(request):
    texto = request.data.get('texto')
    voz = request.data.get('voz', 'alloy')
    
    if not texto:
        return Response({
            'status': 'error', 
            'message': 'El texto es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Crear el directorio temporal si no existe
        audio_dir = 'media/temp_audio'
        os.makedirs(audio_dir, exist_ok=True)
        
        # Generar un nombre único para el archivo
        file_uuid = uuid.uuid4()
        output_file = f"{audio_dir}/tts_{file_uuid}.mp3"
        
        ai_service = AIService()
        result = ai_service.text_to_speech(texto, voice=voz, output_file=output_file)
        
        if result:
            audio_url = f"/media/temp_audio/{os.path.basename(output_file)}"
            return Response({
                'status': 'success',
                'message': 'Audio generado exitosamente',
                'audio_url': audio_url
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Error al generar el audio'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        print(f"Error en text_to_speech: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
    request=LoginSerializer,
    responses={200: LoginResponseSerializer}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def unified_login(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')

        # Intentar obtener el usuario por email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Autenticar al usuario
        user = authenticate(username=user.username, password=password)
        
        if user is not None:
            # Verificar si es profesor
            try:
                teacher = TeacherModel.objects.get(user=user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'status': 'success',
                    'message': 'Inicio de sesión exitoso',
                    'token': str(refresh.access_token),
                    'user_type': 'teacher',
                    'user_data': {
                        'id': teacher.id,
                        'name': user.get_full_name(),
                        'email': user.email,
                        'profile_picture': teacher.profile_picture.url if teacher.profile_picture else None
                    }
                })
            except TeacherModel.DoesNotExist:
                # Si no es profesor, verificar si es estudiante
                try:
                    student = StudentModel.objects.get(user=user)
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'status': 'success',
                        'message': 'Inicio de sesión exitoso',
                        'token': str(refresh.access_token),
                        'user_type': 'student',
                        'user_data': {
                            'id': student.id,
                            'name': user.get_full_name(),
                            'email': user.email,
                            'profile_picture': student.profile_picture.url if student.profile_picture else None
                        }
                    })
                except StudentModel.DoesNotExist:
                    return Response({
                        'status': 'error',
                        'message': 'El usuario no tiene un perfil válido'
                    }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'status': 'error',
                'message': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        print("Error en login:", str(e))  # Log para debugging
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentLoginRecordView(generics.ListCreateAPIView):
    queryset = StudentLoginRecord.objects.all()
    serializer_class = StudentLoginRecordSerializer

    def get_queryset(self):
        # Filtra los registros por estudiante si se proporciona student_id
        queryset = StudentLoginRecord.objects.all()
        student_id = self.request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student=student_id)
        return queryset.order_by('-login_date')

class SearchView(generics.GenericAPIView):
    serializer_class = SearchSerializer

    def get(self, request):
        try:
            # Obtener el término de búsqueda
            query = request.query_params.get('q', '').strip()
            
            if not query:
                return Response({
                    'status': 'error',
                    'message': 'Se requiere un término de búsqueda'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Buscar en CourseModel
            cursos = CourseModel.objects.filter(
                Q(course_name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__icontains=query) |
                Q(level__icontains=query)
            )

            # Buscar en ClassModel
            clases = ClassModel.objects.filter(
                Q(class_name__icontains=query) |
                Q(description__icontains=query)
            )

            # Buscar en ClassContentModel
            contenidos = ClassContentModel.objects.filter(
                Q(tittle__icontains=query) |
                Q(instructions__icontains=query) |
                Q(video_transcription__icontains=query) |
                Q(audio_transcription__icontains=query)
            )

            # Buscar en ScenarioModel
            escenarios = ScenarioModel.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(goals__icontains=query) |
                Q(objectives__icontains=query) |
                Q(student_information__icontains=query) |
                Q(vocabulary__icontains=query) |
                Q(key_expressions__icontains=query)
            )

            # Serializar resultados
            resultados = {
                'cursos': CourseModelSerializer(cursos, many=True).data,
                'clases': ClassModelSerializer(clases, many=True).data,
                'contenidos': ClassContentModelSerializer(contenidos, many=True).data,
                'escenarios': ScenarioModelSerializer(escenarios, many=True).data,
                'total_resultados': len(cursos) + len(clases) + len(contenidos) + len(escenarios)
            }

            return Response({
                'status': 'success',
                'message': 'Búsqueda realizada exitosamente',
                'data': resultados
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al realizar la búsqueda: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UnifiedLogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UnifiedLogoutResponseSerializer

    @extend_schema(
        responses={
            200: UnifiedLogoutResponseSerializer,
            500: ErrorResponseSerializer
        },
        description="Cierra la sesión del usuario invalidando su token"
    )
    def post(self, request):
        try:
            if request.auth:
                request.auth.delete()
            
            return Response({
                'status': 'success',
                'message': 'Sesión cerrada exitosamente'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
