from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.http import HttpResponse
from .serializers import CourseModelSerializer, ClassModelSerializer, LayoutModelSerializer, MultipleChoiceModelSerializer,  TrueOrFalseModelSerializer, OrderingTaskModelSerializer, CategoriesTaskModelSerializer, FillInTheGapsTaskModelSerializer
from .models import CourseModel, ClassModel, LayoutModel, MultipleChoiceModel,TrueOrFalseModel, OrderingTaskModel, CategoriesTaskModel, FillInTheGapsTaskModel
from django.core.exceptions import ValidationError
from django.conf import settings
# Create your views here.

    ## API CRUD
class CourseView(viewsets.ModelViewSet):
    serializer_class = CourseModelSerializer
    queryset = CourseModel.objects.all()

class ClassModelViewSet(viewsets.ModelViewSet):
    queryset = ClassModel.objects.all()
    serializer_class = ClassModelSerializer
    #permission_classes = [IsAuthenticated]

    """
        def perform_create(self, serializer):
            serializer.save(course=self.get_object())
    """

class LayoutModelViewSet(viewsets.ModelViewSet):
    queryset = LayoutModel.objects.all()
    serializer_class = LayoutModelSerializer
    #permission_classes = [IsAuthenticated]

class MultipleChoiceModelViewSet(viewsets.ModelViewSet):
    queryset = MultipleChoiceModel.objects.all()
    serializer_class = MultipleChoiceModelSerializer
    #permission_classes = [IsAuthenticated]

class TrueOrFalseModelViewSet(viewsets.ModelViewSet):
    queryset = TrueOrFalseModel.objects.all()
    serializer_class = TrueOrFalseModelSerializer
    #permission_classes = [IsAuthenticated]

class OrderingTaskModelViewSet(viewsets.ModelViewSet):
    queryset = OrderingTaskModel.objects.all()
    serializer_class = OrderingTaskModelSerializer
    #permission_classes = [IsAuthenticated]

class CategoriesTaskModelViewSet(viewsets.ModelViewSet):
    queryset = CategoriesTaskModel.objects.all()
    serializer_class = CategoriesTaskModelSerializer
    #permission_classes = [IsAuthenticated]

class FillInTheGapsTaskModelViewSet(viewsets.ModelViewSet):
    queryset = FillInTheGapsTaskModel.objects.all()
    serializer_class = FillInTheGapsTaskModelSerializer
    #permission_classes = [IsAuthenticated]


def home(request):
    return render(request, 'home.html')

# Vista para crear un curso
def crear_curso(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        level = request.POST.get('level')
        bullet_points = request.POST.get('bullet_points')
        img_cover = request.FILES.get('img_cover')
        scorm_version = request.POST.get('scorm_version')

        try:
            # Validación de los campos
            if not course_name or not description or not category or not level:
                raise ValidationError("Todos los campos son obligatorios.")
            
            bullet_points = bullet_points if bullet_points else '[]'  # Convertir a JSON si está vacío

            # Crear el nuevo curso
            nuevo_curso = CourseModel.objects.create(
                course_name=course_name,
                description=description,
                category=category,
                level=level,
                bullet_points=bullet_points,
                img_cover=img_cover,
                scorm_version=scorm_version
            )
            return redirect('home')  # Redirigir a una página después de crear el curso
        except ValidationError as e:
            return HttpResponse(f"Error: {e}", status=400)

    return render(request, 'crear_curso.html')

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
import json



from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import CourseModel
import zipfile
import os
from io import BytesIO

def course_list(request):
    courses = CourseModel.objects.all()
    return render(request, 'course_list.html', {'courses': courses})

from io import BytesIO
from django.http import HttpResponse
from xml.etree.ElementTree import Element, SubElement, tostring
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from .models import CourseModel, LayoutModel, MultipleChoiceModel, TrueOrFalseModel, OrderingTaskModel, CategoriesTaskModel, FillInTheGapsTaskModel
