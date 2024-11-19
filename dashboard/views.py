from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.http import HttpResponse
from .serializers import CourseModelSerializer, LessonModelSerializer, LayoutModelSerializer, MultipleChoiceModelSerializer,  TrueOrFalseModelSerializer, OrderingTaskModelSerializer, CategoriesTaskModelSerializer, FillInTheGapsTaskModelSerializer
from .models import CourseModel, LessonModel, LayoutModel, MultipleChoiceModel,TrueOrFalseModel, OrderingTaskModel, CategoriesTaskModel, FillInTheGapsTaskModel
from django.core.exceptions import ValidationError
from django.conf import settings
# Create your views here.

    ## API CRUD
class CourseView(viewsets.ModelViewSet):
    serializer_class = CourseModelSerializer
    queryset = CourseModel.objects.all()

class LessonModelViewSet(viewsets.ModelViewSet):
    queryset = LessonModel.objects.all()
    serializer_class = LessonModelSerializer
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

def crear_leccion(request):
    course_id = '1'
    try:
        curso = CourseModel.objects.get(id=course_id)
    except CourseModel.DoesNotExist:
        return HttpResponse("Curso no encontrado.", status=404)

    if request.method == 'POST':
        # Manejar la creación de la lección
        lesson_data = {
            'lesson_name': request.POST.get('lesson_name'),
            'description': request.POST.get('description'),
            'bullet_points': request.POST.get('bullet_points', '[]'),
            'img_cover': request.FILES.get('img_cover'),
            'scorm_version': request.POST.get('scorm_version')
        }

        try:
            # Validar campos básicos
            if not lesson_data['lesson_name'] or not lesson_data['description']:
                raise ValidationError("Los campos nombre y descripción son obligatorios.")

            # Crear la lección
            nueva_leccion = LessonModel.objects.create(
                course=curso,
                **lesson_data
            )

            # Crear el layout para la lección
            layout = LayoutModel.objects.create(
                title=lesson_data['lesson_name'],
                instructions=lesson_data['description']
            )

            # Procesar las tareas
            tasks_data = json.loads(request.POST.get('tasks', '[]'))
            for task in tasks_data:
                task_type = task.get('type')
                if task_type == 'multiple_choice':
                    MultipleChoiceModel.objects.create(
                        layout=layout,
                        instructions=task['instructions'],
                        question=task['question'],
                        answers=task['answers'],
                        order=task['order']
                    )
                elif task_type == 'true_false':
                    TrueOrFalseModel.objects.create(
                        layout=layout,
                        instructions=task['instructions'],
                        questions=task['questions'],
                        order=task['order']
                    )
                elif task_type == 'ordering':
                    OrderingTaskModel.objects.create(
                        layout=layout,
                        instructions=task['instructions'],
                        items=task['items'],
                        order=task['order']
                    )
                elif task_type == 'categories':
                    CategoriesTaskModel.objects.create(
                        layout=layout,
                        instructions=task['instructions'],
                        categories=task['categories'],
                        order=task['order']
                    )
                elif task_type == 'fill_in_the_gaps':
                    FillInTheGapsTaskModel.objects.create(
                        layout=layout,
                        instructions=task['instructions'],
                        text_with_gaps=task['text_with_gaps'],
                        keywords=task['keywords'],
                        order=task['order']
                    )

            return JsonResponse({'success': True, 'message': 'Lección creada exitosamente'})
        
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return render(request, 'crear_leccion.html', {'curso': curso})


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
from .models import CourseModel, LessonModel, LayoutModel, MultipleChoiceModel, TrueOrFalseModel, OrderingTaskModel, CategoriesTaskModel, FillInTheGapsTaskModel

def generate_scorm_manifest(course):
    # Crear la estructura básica del archivo XML de manifiesto SCORM
    manifest = Element('manifest', identifier="com.example.scorm", version=course.scorm_version)

    metadata = SubElement(manifest, 'metadata')
    title = SubElement(metadata, 'title')
    title.text = course.course_name

    organizations = SubElement(manifest, 'organizations')
    organization = SubElement(organizations, 'organization', identifier="org1")
    title = SubElement(organization, 'title')
    title.text = course.course_name

    # Agregar las lecciones y tareas al manifiesto
    for lesson in course.lessons.all():
        lesson_item = SubElement(organization, 'item', identifier=lesson.lesson_name)
        lesson_title = SubElement(lesson_item, 'title')
        lesson_title.text = lesson.lesson_name

        # Agregar tareas de la lección
        for layout in lesson.layouts.all():
            layout_item = SubElement(lesson_item, 'item', identifier=f"layout_{layout.id}")
            layout_title = SubElement(layout_item, 'title')
            layout_title.text = layout.title

    return tostring(manifest)

import os
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.conf import settings
from io import BytesIO
import zipfile
import os
import json
from django.core.files.base import ContentFile

def download_scorm(request, course_id):
    try:
        course = get_object_or_404(CourseModel, id=course_id)
        
        # Crear un buffer temporal para almacenar el archivo ZIP en memoria
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            # Generar y agregar el archivo imsmanifest.xml al ZIP
            manifest_content = generate_scorm_manifest(course)
            zip_file.writestr('imsmanifest.xml', manifest_content)
            
            # Agregar la imagen de portada del curso si existe
            if course.img_cover and os.path.exists(course.img_cover.path):
                arcname = os.path.join('course_covers', os.path.basename(course.img_cover.name))
                zip_file.write(course.img_cover.path, arcname)
            
            # Agregar los recursos de cada lección y tareas asociadas
            for lesson in course.lessons.all():
                # Agregar la imagen de portada de la lección si existe
                if lesson.img_cover and os.path.exists(lesson.img_cover.path):
                    arcname = os.path.join('lesson_covers', os.path.basename(lesson.img_cover.name))
                    zip_file.write(lesson.img_cover.path, arcname)
                
                # Procesar layouts y sus recursos
                for layout in lesson.layouts.all():
                    # Agregar imagen del layout si existe
                    if layout.img_cover and os.path.exists(layout.img_cover.path):
                        arcname = os.path.join('layout_images', os.path.basename(layout.img_cover.name))
                        zip_file.write(layout.img_cover.path, arcname)
                    
                    # Agregar audio si existe
                    if layout.audio and os.path.exists(layout.audio.path):
                        arcname = os.path.join('layout_audio', os.path.basename(layout.audio.name))
                        zip_file.write(layout.audio.path, arcname)
                    
                    # Agregar preguntas como JSON
                    for question in layout.questions.all():
                        question_data = {
                            'instructions': question.instructions,
                            'question': question.question,
                            'answers': question.answers,
                            'order': question.order
                        }
                        question_json = json.dumps(question_data, ensure_ascii=False)
                        zip_file.writestr(
                            f'questions/layout_{layout.id}/question_{question.id}.json',
                            question_json
                        )
                        
            # Agregar archivo index.html básico
            index_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Course Content</title>
                <meta charset="UTF-8">
            </head>
            <body>
                <h1>Course: {}</h1>
                <div id="content">
                    <!-- Content will be loaded dynamically -->
                </div>
            </body>
            </html>
            """.format(course.course_name)
            zip_file.writestr('index.html', index_html)

        # Preparar la respuesta
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{course.course_name}_SCORM.zip"'
        return response
        
    except Exception as e:
        # Log the error here if you have logging configured
        print(f"Error creating SCORM package: {str(e)}")
        raise Http404(f"Error creating SCORM package: {str(e)}")