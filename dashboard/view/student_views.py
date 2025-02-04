from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import StudentModel, StudentLoginRecord, StudentNoteModel, VocabularyEntryModel, CourseModel
from ..serializers import StudentModelSerializer, CourseModelSerializer, StudentCoursesSerializer, StudentLoginRecordSerializer, StudentNoteModelSerializer, VocabularyEntryModelSerializer
from rest_framework.decorators import api_view, action
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.models import User
   
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
            # Verificar si ya existe un usuario con ese email
            email = serializer.validated_data.get('email')
            if User.objects.filter(email=email).exists():
                return Response({
                    'status': 'error',
                    'message': 'Ya existe un estudiante registrado con este email'
                }, status=status.HTTP_400_BAD_REQUEST)
                
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
                'message': str(e)
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

            
class StudentViewSet(generics.GenericAPIView):
    queryset = StudentModel.objects.all()
    serializer_class = StudentModelSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return StudentModel.objects.get(user=self.request.user)
        except StudentModel.DoesNotExist:
            raise StudentModel.DoesNotExist('Student not found for this user')

    def patch(self, request, *args, **kwargs):
        print(f"\nRecibida solicitud PATCH para actualizar perfil")
        print(f"Usuario: {request.user}")
        print(f"Datos recibidos: {request.data}")
        
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                print("Datos válidos, guardando...")
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Perfil actualizado exitosamente',
                    'data': serializer.data
                })
            else:
                print(f"Errores de validación: {serializer.errors}")
                return Response({
                    'status': 'error',
                    'message': 'Error en la validación',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except StudentModel.DoesNotExist:
            print("Estudiante no encontrado")
            return Response({
                'status': 'error',
                'message': 'Estudiante no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Verificar si el usuario tiene permisos para eliminar
            if not request.user.is_staff and request.user != instance.user:
                return Response({
                    'status': 'error',
                    'message': 'No tienes permiso para eliminar este estudiante'
                }, status=status.HTTP_403_FORBIDDEN)
                
            user = instance.user  # Guardamos referencia al usuario
            instance.delete()     # Eliminamos el StudentModel
            user.delete()         # Eliminamos también el User asociado
            
            return Response({
                'status': 'success',
                'message': 'Estudiante eliminado exitosamente'
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

class StudentCoursesView(generics.GenericAPIView):
    serializer_class = StudentCoursesSerializer

    def get(self, request, student_id):
        """
        Obtiene la lista de cursos en los que está inscrito el estudiante
        """
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

    def post(self, request, student_id):
        """
        Inscribe al estudiante en un curso
        """
        try:
            student = StudentModel.objects.get(id=student_id)
            course_id = request.data.get('course_id')
            
            if not course_id:
                return Response({
                    'status': 'error',
                    'message': 'Se requiere el ID del curso'
                }, status=status.HTTP_400_BAD_REQUEST)

            course = CourseModel.objects.get(id=course_id)
            
            if course in student.courses.all():
                return Response({
                    'status': 'error',
                    'message': 'El estudiante ya está inscrito en este curso'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            student.courses.add(course)
            return Response({
                'status': 'success',
                'message': 'Inscripción exitosa'
            }, status=status.HTTP_201_CREATED)

        except StudentModel.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Estudiante no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
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

    def delete(self, request, student_id):
        """
        Elimina la inscripción de un estudiante a un curso
        """
        try:
            student = StudentModel.objects.get(id=student_id)
            course_id = request.data.get('course_id')
            
            if not course_id:
                return Response({
                    'status': 'error',
                    'message': 'Se requiere el ID del curso'
                }, status=status.HTTP_400_BAD_REQUEST)

            course = CourseModel.objects.get(id=course_id)
            
            if course not in student.courses.all():
                return Response({
                    'status': 'error',
                    'message': 'El estudiante no está inscrito en este curso'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            student.courses.remove(course)
            return Response({
                'status': 'success',
                'message': 'Inscripción eliminada exitosamente'
            }, status=status.HTTP_200_OK)

        except StudentModel.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Estudiante no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
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
