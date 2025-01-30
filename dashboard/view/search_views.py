from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from ..models import CourseModel, ClassModel, ClassContentModel, ScenarioModel
from ..serializers import CourseModelSerializer, ClassModelSerializer, ClassContentModelSerializer, ScenarioModelSerializer, SearchSerializer
from django.db.models import Q


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
