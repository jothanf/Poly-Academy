from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.http import HttpResponse
from .serializers import CourseModelSerializer, ClassModelSerializer, LayoutModelSerializer, MultipleChoiceModelSerializer,  TrueOrFalseModelSerializer, OrderingTaskModelSerializer, CategoriesTaskModelSerializer, FillInTheGapsTaskModelSerializer, VideoLayoutModelSerializer, TextBlockLayoutModelSerializer, MediaModelSerializer, MultimediaBlockVideoModelSerializer, ClassContentModelSerializer
from .models import CourseModel, ClassModel, LayoutModel, MultipleChoiceModel,TrueOrFalseModel, OrderingTaskModel, CategoriesTaskModel, FillInTheGapsTaskModel, VideoLayoutModel, TextBlockLayoutModel, MediaModel, MultimediaBlockVideoModel, ClassContentModel
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework import generics
import logging
from django.core.files.storage import default_storage
import json

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
            response = super().update(request, *args, **kwargs)
            return Response({
                'status': 'success',
                'message': f'{self.model_name} actualizado exitosamente',
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
                'message': f'Error al actualizar {self.model_name}',
                'campos_con_error': error_details,
                'tipo_error': 'validación'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al actualizar {self.model_name}',
                'detalle_error': str(e),
                'tipo_error': 'sistema'
            }, status=status.HTTP_400_BAD_REQUEST)

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

class CourseView(BaseModelViewSet):
    serializer_class = CourseModelSerializer
    queryset = CourseModel.objects.all()
    model_name = 'curso'
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        try:
            imagen = request.FILES.get('imagen')
            response = super().create(request, *args, **kwargs)
            return Response({
                'status': 'success',
                'message': 'Curso creado exitosamente',
                'data': response.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Error al crear el curso',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

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

class ClasDeleteView(APIView):
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

class ClassTasksView(APIView):
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

class TaskLayoutDetailView(APIView):
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
            return Response({
                'status': 'error',
                'message': 'Error al crear el contenido de clase',
                'detalle_error': str(e),
                'tipo_error': 'sistema'
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
