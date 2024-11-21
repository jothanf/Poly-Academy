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

class CourseModel(models.Model):
    cover = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    course_name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=100)
    level = models.CharField(max_length=100)
    bullet_points = models.JSONField(help_text="Formato: ['punto 1', 'punto 2', ...]")
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
    title = models.CharField(max_length=200)
    instructions = models.TextField(null=True, blank=True)
    cover = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    audio = models.FileField(upload_to='class_audio/', null=True, blank=True)
    audio_script = models.TextField()

    ##Multiple Choice Task

class MultipleChoiceModel(models.Model):
    layout = models.ForeignKey(LayoutModel, on_delete=models.CASCADE, related_name="questions")
    instructions = models.TextField(null=True, blank=True)
    question = models.CharField(max_length=200)
    answers = models.JSONField(
        help_text="Formato: [{'text': 'respuesta', 'is_correct': true/false}, ...]"
    )
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('layout', 'order')
        ordering = ['order']

    ##True or False Task

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

class TrueOrFalseModel(models.Model):
    layout = models.ForeignKey(LayoutModel, on_delete=models.CASCADE, related_name="true_or_false_tasks")
    instructions = models.TextField(null=True, blank=True)
    #questions = models.JSONField(validators=[validate_questions_true_false])
    questions = models.JSONField()
    order = models.PositiveIntegerField(default=0, help_text="Orden de aparición de la tarea.")

    class Meta:
        ordering = ['order']
        unique_together = ('layout', 'order')

    def __str__(self):
        # Muestra la primera pregunta para una vista previa
        first_question = self.questions.get("questions", [{}])[0]
        statement = first_question.get("statement", "Sin declaración")
        state = first_question.get("state", 3)
        state_text = {1: "Verdadero", 2: "Falso", 3: "No establecido"}
        return f"{statement} - {state_text.get(state, 'No establecido')}"

    ##Ordering Task

def validate_items_ordering(items):
    if not isinstance(items, dict) or "items" not in items:
        raise ValidationError("El JSON debe tener una clave 'items' que contenga una lista de elementos.")
    
    for item in items.get("items", []):
        if not isinstance(item, dict) or "id" not in item or "description" not in item:
            raise ValidationError("Cada elemento en 'items' debe tener un 'id' y una 'description'.")

class OrderingTaskModel(models.Model):
    layout = models.ForeignKey(LayoutModel, related_name="ordering_tasks", on_delete=models.CASCADE)
    instructions = models.TextField(null=True, blank=True)
    #items = models.JSONField(help_text="Lista de elementos a ordenar en formato JSON.", validators=[validate_items_ordering])
    items = models.JSONField(help_text="Lista de elementos a ordenar en formato JSON.")
    order = models.PositiveIntegerField(default=0, help_text="Orden de aparición de la tarea.")

    class Meta:
        ordering = ['order']
        unique_together = ('layout', 'order')

    def __str__(self):
        return f"Tarea de Ordenar - {self.instructions[:30]}"

    ## Categories Task

def validate_categories(categories):
    if not isinstance(categories, dict) or "categories" not in categories:
        raise ValidationError("El JSON debe tener una clave 'categories' que contenga una lista de categorías.")

    for category in categories.get("categories", []):
        if not isinstance(category, dict) or "name" not in category or "items" not in category:
            raise ValidationError("Cada categoría debe tener una clave 'name' y una lista de 'items'.")
        if not isinstance(category["items"], list):
            raise ValidationError("La clave 'items' debe ser una lista.")

class CategoriesTaskModel(models.Model):
    layout = models.ForeignKey(LayoutModel, related_name="categories_tasks", on_delete=models.CASCADE)
    instructions = models.TextField(null=True, blank=True)
    #categories = models.JSONField(validators=[validate_categories])
    categories = models.JSONField()
    order = models.PositiveIntegerField(default=0, help_text="Orden de aparición de la tarea.")

    class Meta:
        ordering = ['order']
        unique_together = ('layout', 'order')

    def __str__(self):
        return f"Tarea de Ordenar - {self.instructions[:30]}"

    ## Fill in de Gaps Task

class FillInTheGapsTaskModel(models.Model):
    layout = models.ForeignKey(LayoutModel, on_delete=models.CASCADE, related_name="fill_in_the_gaps_tasks")
    instructions = models.TextField(null=True, blank=True)
    text_with_gaps = models.TextField(help_text="Texto con espacios para completar. Usa '{gap}' para indicar los espacios.")
    keywords = models.JSONField(help_text="Palabras claves en formato JSON, en el orden de aparición de los espacios.")
    order = models.PositiveIntegerField(default=0, help_text="Orden de aparición de la tarea.")

    class Meta:
        ordering = ['order']
        unique_together = ('layout', 'order')

    def __str__(self):
        return f"Tarea de Llenar Espacios - {self.instructions[:30]}"

    
class TextBlockModel(models.Model):
    lesson = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='text_blocks')
    title = models.CharField(max_length=200, help_text="Título del bloque de texto")
    instructions = models.TextField(null=True, blank=True)
    content = models.TextField(help_text="Contenido de texto")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class VideoModel(models.Model):
    title = models.CharField(max_length=200, help_text="Título del video")
    instructions = models.TextField(null=True, blank=True)
    video_file = models.FileField(upload_to='videos/', null=True, blank=True, help_text="Archivo de video")
    script = models.TextField(help_text="Transcripción de lo que se dice en el video")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

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