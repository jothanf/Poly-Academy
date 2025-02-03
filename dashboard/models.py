from django.db import models
from django.core.exceptions import ValidationError
import os
import zipfile
from django.conf import settings
from xml.etree.ElementTree import Element, SubElement, tostring
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class TeacherModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to='teacher_profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.user.email

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
    publish = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.course_name

class ClassModel(models.Model):
    cover = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    class_name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, related_name="classes")
    bullet_points = models.JSONField(help_text="Formato: ['punto 1', 'punto 2', ...]", blank=True, null=True)
    publish = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.class_name
    

class StudentModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(CourseModel, related_name='enrolled_students', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to='student_profile_pictures/', null=True, blank=True)


class LayoutModel(models.Model):
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='layouts')
    tittle = models.CharField(max_length=300, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    cover = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    audio = models.FileField(upload_to='class_audio/', null=True, blank=True)
    audio_script = models.TextField(null=True, blank=True)

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
    image = models.ImageField(upload_to='content_images/', null=True, blank=True, max_length=500)
    video = models.FileField(upload_to='content_videos/', null=True, blank=True, max_length=500)
    video_transcription = models.TextField(null=True, blank=True)
    embed_video = models.URLField(null=True, blank=True)
    audio = models.FileField(upload_to='content_audios/', null=True, blank=True, max_length=500)
    audio_transcription = models.TextField(null=True, blank=True)
    pdf = models.FileField(upload_to='content_pdfs/', null=True, blank=True, max_length=500)
    
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
        return f"{self.get_content_type_display()} - {self.tittle or 'Sin título'}"

class ScenarioModel(models.Model):
    class_id = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='scenarios')
    cover = models.ImageField(upload_to='scenario_covers/', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    goals = models.TextField(null=True, blank=True)
    objectives = models.TextField(null=True, blank=True)
    student_information = models.TextField(null=True, blank=True)
    role_polly = models.CharField(max_length=200, null=True, blank=True)
    role_student = models.CharField(max_length=200, null=True, blank=True)
    conversation_starter = models.TextField(blank=True, null=True)
    vocabulary = models.TextField(null=True, blank=True)
    key_expressions = models.TextField(null=True, blank=True)
    end_conversation = models.TextField(null=True, blank=True)
    end_conversation_saying = models.TextField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    scoring = models.TextField(null=True, blank=True)
    additional_info = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"
"""
class FormattedTextModel(models.Model):
    class_id = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='formatted_texts')
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
"""


class StudentProgressModel(models.Model):
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, related_name='progress')
    class_content = models.ForeignKey(ClassContentModel, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)
    answers = models.JSONField(null=True, blank=True)  # Almacena las respuestas del estudiante

    class Meta:
        unique_together = ['student', 'class_content']


class StudentNoteModel(models.Model):
    NOTE_TYPES = [
        ('vocabulary', 'Vocabulary'),
        ('grammar', 'Grammar'),
        ('expressions', 'Expressions'),
        ('general', 'General Note'),
    ]

    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, related_name='notes')
    class_id = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='student_notes', null=True, blank=True)
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general')
    
    # For organization and search
    tags = models.JSONField(null=True, blank=True, help_text="List of tags to categorize the note")
    highlighted = models.BooleanField(default=False)
    color = models.CharField(max_length=7, null=True, blank=True, help_text="HEX color code for the note")
    
    # For references
    related_url = models.URLField(null=True, blank=True)
    related_content = models.ForeignKey(
        ClassContentModel, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='related_notes'
    )
    
    # Time fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Student Note'
        verbose_name_plural = 'Student Notes'

    def __str__(self):
        return f"Note from {self.student.user.username}: {self.title}"



class VocabularyEntryModel(models.Model):
    PROFICIENCY_LEVELS = [
        (1, 'Principiante'),      # Apenas conoce la palabra
        (2, 'Básico'),           # Reconoce y entiende
        (3, 'Intermedio'),       # Puede usar en contextos simples
        (4, 'Avanzado'),         # Usa con confianza
        (5, 'Dominado')          # Dominio completo
    ]

    ENTRY_TYPES = [
        ('word', 'Palabra'),
        ('phrase', 'Frase'),
        ('expression', 'Expresión'),
        ('slang', 'Modismo'),
        ('idiom', 'Frase hecha')
    ]

    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, related_name='vocabulary')
    class_model = models.ForeignKey(ClassModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='vocabulary_entries')
    
    # Contenido principal
    term = models.CharField(max_length=200, help_text="Palabra o frase a aprender")
    translation = models.CharField(max_length=200, help_text="Traducción a tu idioma nativo")
    context = models.TextField(null=True, blank=True, help_text="Ejemplo de uso en contexto")
    notes = models.TextField(null=True, blank=True, help_text="Notas personales sobre el uso")
    
    # Categorización
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES, default='word')
    tags = models.JSONField(null=True, blank=True, help_text="Etiquetas para organizar el vocabulario")
    category = models.CharField(max_length=100, null=True, blank=True, help_text="Categoría temática")
    
    # Progreso de aprendizaje
    proficiency_level = models.IntegerField(
        choices=PROFICIENCY_LEVELS, 
        default=1,
        help_text="Nivel de dominio actual"
    )
    times_practiced = models.PositiveIntegerField(default=0, help_text="Número de veces practicada")
    last_practiced = models.DateTimeField(null=True, blank=True)
    next_review = models.DateTimeField(null=True, blank=True, help_text="Fecha sugerida para próxima revisión")
    
    # Multimedia
    audio_pronunciation = models.FileField(
        upload_to='vocabulary_audio/', 
        null=True, 
        blank=True,
        help_text="Audio de pronunciación"
    )
    image = models.ImageField(
        upload_to='vocabulary_images/', 
        null=True, 
        blank=True,
        help_text="Imagen relacionada"
    )
    
    # Metadatos
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Entrada de Vocabulario'
        verbose_name_plural = 'Entradas de Vocabulario'
        indexes = [
            models.Index(fields=['student', 'term']),
            models.Index(fields=['proficiency_level']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.term} - {self.translation}"

    def update_proficiency(self, success_rate):
        """
        Actualiza el nivel de dominio basado en el éxito de la práctica
        success_rate: float entre 0 y 1
        """
        if success_rate > 0.8 and self.proficiency_level < 5:
            self.proficiency_level += 1
        elif success_rate < 0.4 and self.proficiency_level > 1:
            self.proficiency_level -= 1
        
        self.times_practiced += 1
        self.last_practiced = timezone.now()
        
        # Calcula próxima revisión usando espaciado repetitivo
        days_until_review = {
            1: 1,      # Principiante: revisar al día siguiente
            2: 3,      # Básico: revisar en 3 días
            3: 7,      # Intermedio: revisar en una semana
            4: 14,     # Avanzado: revisar en dos semanas
            5: 30,     # Dominado: revisar en un mes
        }
        
        self.next_review = timezone.now() + timezone.timedelta(
            days=days_until_review[self.proficiency_level]
        )
        
        self.save()

class CourseProgressModel(models.Model):
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)
    progress_percentage = models.FloatField(default=0)
    average_score = models.FloatField(default=0)
    completed = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'course']

class ClassProgressModel(models.Model):
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, related_name='class_progress')
    class_model = models.ForeignKey(ClassModel, on_delete=models.CASCADE)
    progress_percentage = models.FloatField(default=0)
    average_score = models.FloatField(default=0)
    completed = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'class_model']

class StudentActivityLogModel(models.Model):
    ACTIVITY_TYPES = [
        ('start_content', 'Inicio de contenido'),
        ('complete_content', 'Completó contenido'),
        ('submit_answer', 'Envió respuesta'),
        ('retry_content', 'Reintentó contenido'),
        ('view_feedback', 'Vio retroalimentación'),
    ]

    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, related_name='activity_logs')
    class_content = models.ForeignKey(ClassContentModel, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    score = models.FloatField(null=True, blank=True)
    details = models.JSONField(null=True, blank=True)  # Para almacenar detalles específicos de la actividad
    timestamp = models.DateTimeField(auto_now_add=True)

class StudentLoginRecord(models.Model):
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, related_name='login_records')
    login_date = models.DateField(auto_now_add=True)
