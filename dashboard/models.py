from django.db import models
from django.core.exceptions import ValidationError
import os
import zipfile
from django.conf import settings
from xml.etree.ElementTree import Element, SubElement, tostring
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

import os
import zipfile
from django.conf import settings
from xml.etree.ElementTree import Element, SubElement, tostring
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

class MediaModel(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    ]

    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to='task_media/')
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.media_type} - {self.file.name}"

class CourseModel(models.Model):
    cover = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    course_name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    level = models.CharField(max_length=100, null=True, blank=True)
    bullet_points = models.JSONField(help_text="Formato: ['punto 1', 'punto 2', ...]", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ClassModel(models.Model):
    cover = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    class_name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, related_name="classes")
    bullet_points = models.JSONField(help_text="Formato: ['punto 1', 'punto 2', ...]", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.class_name

class LayoutModel(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='layouts')
    tittle = models.CharField(max_length=300, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    cover = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    audio = models.FileField(upload_to='class_audio/', null=True, blank=True)
    audio_script = models.TextField(null=True, blank=True)

    ##Multiple Choice Task

class MultipleChoiceModel(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name="multiple_choice_tasks")
    ##layout = models.ForeignKey(LayoutModel, on_delete=models.CASCADE, related_name="questions")
    tittle = models.CharField(max_length=200, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    script = models.TextField(null=True, blank=True)
    question = models.JSONField()
    cover = models.ImageField(upload_to='cover_multiple_choice_tasks/', null=True, blank=True)
    audio = models.FileField(upload_to='audio_multiple_choice_tasks/', null=True, blank=True)
    ##media = models.ManyToManyField(MediaModel, related_name="multiple_choice_tasks", blank=True)
    order = models.PositiveIntegerField(default=0)
    stats = models.BooleanField(default=False)

    ##True or False Task

"""
def validate_questions_true_false(questions):
    if not isinstance(questions, dict) or "questions" not in questions:
        raise ValidationError("El JSON debe tener una clave 'questions' que contenga una lista de preguntas.")
    
    for question in questions.get("questions", []):
        if not isinstance(question, dict):
            raise ValidationError("Cada pregunta debe ser un objeto JSON.")
        if "statement" not in question or "state" not in question:
            raise ValidationError("Cada pregunta debe tener una clave 'statement' y una clave 'state'.")
        if question["state"] not in [1, 2, 3]:
            raise ValidationError("El campo 'state' debe ser 1 (true), 2 (false), o 3 (not_state).")
"""

class TrueOrFalseModel(models.Model):
    #layout = models.ForeignKey(LayoutModel, on_delete=models.CASCADE, related_name="true_or_false_tasks")
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name="true_or_false_tasks")
    tittle = models.CharField(max_length=200, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    questions = models.JSONField()
    media = models.ManyToManyField(MediaModel, related_name="true_or_false_tasks", blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Orden de aparición de la tarea.")


  


class OrderingTaskModel(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name="ordering_tasks")
    tittle = models.CharField(max_length=200, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    #items = models.JSONField(help_text="Lista de elementos a ordenar en formato JSON.", validators=[validate_items_ordering])
    items = models.JSONField(help_text="Lista de elementos a ordenar en formato JSON.")
    media = models.ManyToManyField(MediaModel, related_name="ordering_tasks", blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Orden de aparición de la tarea.")

    ## Categories Task
"""
def validate_categories(categories):
    if not isinstance(categories, dict) or "categories" not in categories:
        raise ValidationError("El JSON debe tener una clave 'categories' que contenga una lista de categorías.")

    for category in categories.get("categories", []):
        if not isinstance(category, dict) or "name" not in category or "items" not in category:
            raise ValidationError("Cada categoría debe tener una clave 'name' y una lista de 'items'.")
        if not isinstance(category["items"], list):
            raise ValidationError("La clave 'items' debe ser una lista.")
"""
class CategoriesTaskModel(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name="categories_tasks")
    tittle = models.CharField(max_length=200, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    #categories = models.JSONField(validators=[validate_categories])
    categories = models.JSONField()
    media = models.ManyToManyField(MediaModel, related_name="categories_tasks", blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Orden de aparición de la tarea.")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Tarea de Ordenar - {self.instructions[:30]}"

    ## Fill in de Gaps Task

class FillInTheGapsTaskModel(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name="fill_in_the_gaps_tasks")
    tittle = models.CharField(max_length=200, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    text_with_gaps = models.TextField(help_text="Texto con espacios para completar. Usa '{gap}' para indicar los espacios.")
    keywords = models.JSONField(help_text="Palabras claves en formato JSON, en el orden de aparición de los espacios.")
    order = models.PositiveIntegerField(default=0, help_text="Orden de aparición de la tarea.")
    media = models.ManyToManyField(MediaModel, related_name="fill_in_the_gaps_tasks", blank=True)


    
class TextBlockLayoutModel(models.Model):
    lesson = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='text_blocks')
    tittle = models.CharField(max_length=200, help_text="Título del bloque de texto", null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    content = models.TextField(help_text="Contenido de texto")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class VideoLayoutModel(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='videos')
    tittle = models.CharField(max_length=200, help_text="Título del video")
    instructions = models.TextField(null=True, blank=True)
    video_file = models.FileField(upload_to='videos/', null=True, blank=True, help_text="Archivo de video")
    script = models.TextField(help_text="Transcripción de lo que se dice en el video", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class MultimediaBlockVideoModel(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name="multimedia_block_videos_uploaded")
    tittle = models.CharField(max_length=200, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    video = models.FileField(upload_to='multimedia_block_videos/', null=True, blank=True, help_text="Archivo de video")
    script = models.TextField(help_text="Transcripción de lo que se dice en el video", null=True, blank=True)
    cover = models.ImageField(upload_to='multimedia_block_videos/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)


class MultimediaBlockAudioModel(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name="multimedia_block_audios")
    tittle = models.CharField(max_length=200, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    audio = models.FileField(upload_to='multimedia_block_audios/', null=True, blank=True, help_text="Archivo de audio")
    script = models.TextField(help_text="Transcripción de lo que se dice en el video", null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

class MultimediaBlockVideoEmbedModel(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name="multimedia_block_videos_embedded")
    tittle = models.CharField(max_length=200, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    link_video = models.URLField(null=True, blank=True)
    cover = models.ImageField(upload_to='multimedia_block_videos/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

class MultimediaBlockAttachmentModel(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name="multimedia_block_attachments")
    tittle = models.CharField(max_length=200, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    link_attachment = models.URLField(null=True, blank=True)
    text_attachment = models.TextField(null=True, blank=True)
    file_attachment = models.FileField(upload_to='attachments/', null=True, blank=True, help_text="Archivo adjunto (pdf, txt, etc.)")
    cover = models.ImageField(upload_to='multimedia_block_videos/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

"""
Course Json:
    {
        "bullet_points": [
            {
                "text": "Bullet point 1"
            },
            {
                "text": "Bullet point 2"
            },
            {
                "text": "Bullet point 3"
            }
        ]
    }
"""

"""
MultipleChoice Json:
    {
    "answers": [
        {
            "text": "Answer 1",
            "is_correct": true
        },
        {
            "text": "Answer 2",
            "is_correct": false
        },
        {
            "text": "Answer 3",
            "is_correct": false
        },
        {
            "text": "Answer 4",
            "is_correct": true
        }
    ]
}

"""

"""
True or False Json:
    {
    "questions": [
        {
            "statement": "The Earth is flat.",
            "state": 2 // 1 for true, 2 for false, 3 for not stated
        },
        {
            "statement": "Water boils at 100 degrees Celsius.",
            "state": 1
        },
        {
            "statement": "Cats can fly.",
            "state": 3
        }
    ]
"""
"""
OrderingTask Json:
   {
    "items": [
            {
                "id": 1,
                "description": "Item A"
            },
            {
                "id": 2,
                "description": "Item B"
            },
            {
                "id": 3,
                "description": "Item C"
            }
        ]
    }

"""
"""
CategoriesTask Json:
    {
        "categories": [
            {
                "name": "Category 1",
                "items": [
                    "Item 1A",
                    "Item 1B",
                    "Item 1C"
                ]
            },
            {
                "name": "Category 2",
                "items": [
                    "Item 2A",
                    "Item 2B",
                    "Item 2C"
                ]
            }
        ]
    }
"""
"""
Fill in de Gaps Json:
    {
        "text_with_gaps": "The {gap/gas}id=1 is round and orbits the {gap}.",
        "keywords": [
            {
                "id":1
                
            }
            "Earth",
            "Sun"
        ]
    }
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
import os
import uuid

class ClassContentModel(models.Model):
    CONTENT_TYPES = [
        #Overlay Tasks
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True or False'),
        ('fill_gaps', 'Fill in the Gaps'),
        ('word_bank', 'Word Bank'),
        ('drop_down_text', 'Drop Down Text'),
        ('ordering', 'Ordering'),
        ('sorting', 'Sorting'),
        ('category', 'Category'),
        ('matching', 'Matching'),
        #Interactive activities
        ('flashcards', 'Flashcards'),
        ('table', 'Table'),
        ('accordion', 'Accordion'),
        ('tabs', 'Tabs'),
        ('button_stack', 'Button Stack'),
        ('process','Process'),
        ('timeline', 'Timeline'),
        #Knowledge Check
        ('multiple_choice_knowledge_check', 'Multiple Choice Knowledge Check'),
        ('true_false_knowledge_check', 'True or False Knowledge Check'),
        ('fill_gaps_knowledge_check', 'Fill in the Gaps Knowledge Check'),
        ('word_bank_knowledge_check', 'Word Bank Knowledge Check'),
        ('drop_down_text_knowledge_check', 'Drop Down Text Knowledge Check'),
        ('ordering_knowledge_check', 'Ordering Knowledge Check'),
        ('sorting_knowledge_check', 'Sorting Knowledge Check'),
        ('categories_knowledge_check', 'Categories Knowledge Check'),
        ('matching_knowledge_check', 'Matching Knowledge Check'),
        ('word_order_knowledge_check', 'Word Order Knowledge Check'),
        ('picture_matching_knowledge_check', 'Picture Matching Knowledge Check'),
        ('picture_labeling_knowledge_check', 'Picture Labeling Knowledge Check'),
        #Text Blocks
        ('text_block', 'Text Block'),
        ('text_article', 'Text Article'),
        ('text_quote', 'Text Quote'),
        ('text_highlighted', 'Text Highlighted'),
        ('info_box', 'Info Box'),
        ('icon_list', 'Icon List'),
        #Multimedia
        ('image', 'Imagen'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('video_embed', 'Video Embebido'),
        ('attachment', 'Archivo Adjunto'),
        #IA Chat
        ('ia_chat', 'IA Chat'),
    ]

    MEDIA_TYPES = [
        ('image', 'Imagen'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('pdf', 'Documento PDF'),
    ]

    class_id = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='contents')
    
    content_type = models.CharField(max_length=100, choices=CONTENT_TYPES)
    tittle = models.CharField(max_length=500, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    
    content_details = models.JSONField(null=True, blank=True)
    
    # Campos para multimedia en JSON
    multimedia = models.JSONField(null=True, blank=True)
    image = models.ImageField(upload_to='content_images/', null=True, blank=True)
    video = models.FileField(upload_to='content_videos/', null=True, blank=True)
    video_transcription = models.TextField(null=True, blank=True)
    embed_video = models.URLField(null=True, blank=True)
    audio = models.FileField(upload_to='content_audios/', null=True, blank=True)
    audio_transcription = models.TextField(null=True, blank=True)
    pdf = models.FileField(upload_to='content_pdfs/', null=True, blank=True)
    
    order = models.PositiveIntegerField(default=0)
    stats = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save_multimedia_file(self, file, media_type):
        
        ##Guarda un archivo multimedia y devuelve su información
        
        if not file:
            return None

        # Generar un nombre de archivo único
        ext = os.path.splitext(file.name)[1]
        filename = f"content_media/{uuid.uuid4()}{ext}"
        
        # Guardar el archivo
        path = default_storage.save(filename, file)
        
        return {
            'name': file.name,
            'url': default_storage.url(path),
            'path': path,
            'media_type': media_type,
            'size': file.size
        }

    def process_multimedia(self, multimedia_data):
        
        ##Procesa los datos multimedia
        
        processed_multimedia = []
        
        if not isinstance(multimedia_data, list):
            raise ValidationError("Los datos multimedia deben ser una lista")
        
        for media_item in multimedia_data:
            # Validar el tipo de medio
            media_type = media_item.get('media_type')
            if media_type not in dict(self.MEDIA_TYPES):
                raise ValidationError(f"Tipo de medio no válido: {media_type}")
            
            # Procesar archivos
            file = media_item.get('file')
            if file:
                file_info = self.save_multimedia_file(file, media_type)
                media_item['file_info'] = file_info
            
            processed_multimedia.append(media_item)
        
        return processed_multimedia

    def clean(self):
        # Validar y procesar multimedia si está presente
        if self.multimedia:
            self.multimedia = self.process_multimedia(self.multimedia)
        
        # Validaciones existentes para content_details
        # ... (mantén las validaciones anteriores)

    class Meta:
        ordering = ['order']
        verbose_name = 'Contenido de Clase'
        verbose_name_plural = 'Contenidos de Clase'

    def __str__(self):
        return f"{self.get_content_type_display()} - {self.title or 'Sin título'}"

class ScenarioModel(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='scenarios')
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    description = models.TextField()
    goals = models.JSONField(null=True, blank=True)
    vocabulary = models.JSONField(null=True, blank=True)
    key_expressions = models.JSONField(null=True, blank=True)
    additional_info_objective = models.JSONField(null=True, blank=True)
    limitations_student = models.TextField()
    role_student = models.CharField(max_length=200)
    role_polly = models.CharField(max_length=200)
    instructions_polly = models.JSONField(null=True, blank=True)
    limitations_polly = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

class FormattedTextModel(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='formatted_texts')
    title = models.CharField(max_length=200, null=True, blank=True)
    content = models.TextField(help_text="Contenido con formato HTML/TipTap")
    instructions = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Texto Formateado'
        verbose_name_plural = 'Textos Formateados'

    def __str__(self):
        return f"Texto Formateado - {self.title or 'Sin título'}"

