from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import CourseModel
from ..serializers import CourseModelSerializer, StudentModelSerializer
from django.shortcuts import render
from rest_framework import generics



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

def course_list(request):
    courses = CourseModel.objects.all().order_by('-created_at')
    return render(request, 'course_list.html', {'courses': courses}) 


class CourseStudentsView(generics.GenericAPIView):
    serializer_class = StudentModelSerializer

    def get(self, request, course_id):
        """
        Obtiene la lista de estudiantes inscritos en un curso específico
        """
        try:
            course = CourseModel.objects.get(id=course_id)
            students = course.enrolled_students.all()
            serializer = self.get_serializer(students, many=True)
            
            return Response({
                'status': 'success',
                'message': 'Estudiantes obtenidos exitosamente',
                'data': {
                    'course_name': course.course_name,
                    'total_students': students.count(),
                    'students': serializer.data
                }
            }, status=status.HTTP_200_OK)
            
        except CourseModel.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Curso no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
