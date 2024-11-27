from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.http import HttpResponse
from .serializers import CourseModelSerializer, ClassModelSerializer, LayoutModelSerializer, MultipleChoiceModelSerializer,  TrueOrFalseModelSerializer, OrderingTaskModelSerializer, CategoriesTaskModelSerializer, FillInTheGapsTaskModelSerializer
from .models import CourseModel, ClassModel, LayoutModel, MultipleChoiceModel,TrueOrFalseModel, OrderingTaskModel, CategoriesTaskModel, FillInTheGapsTaskModel
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
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
            super().destroy(request, *args, **kwargs)
            return Response({
                'status': 'success',
                'message': f'{self.model_name} eliminado exitosamente'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al eliminar {self.model_name}',
                'error': str(e)
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

class LayoutModelViewSet(BaseModelViewSet):
    queryset = LayoutModel.objects.all()
    serializer_class = LayoutModelSerializer
    model_name = 'layout'

class MultipleChoiceModelViewSet(BaseModelViewSet):
    queryset = MultipleChoiceModel.objects.all()
    serializer_class = MultipleChoiceModelSerializer
    model_name = 'modelo de elección múltiple'

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
