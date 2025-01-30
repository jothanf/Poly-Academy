from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import generics
from ..models import LayoutModel
from ..serializers import (
    LayoutModelSerializer,
)

"""
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
"""