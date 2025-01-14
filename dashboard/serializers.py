from rest_framework import serializers
from .models import CourseModel, ClassModel, LayoutModel, MultipleChoiceModel, TrueOrFalseModel, OrderingTaskModel, CategoriesTaskModel, FillInTheGapsTaskModel, VideoLayoutModel, TextBlockLayoutModel, MediaModel, MultimediaBlockVideoModel, ClassContentModel, ScenarioModel, FormattedTextModel, StudentModel, StudentNoteModel, VocabularyEntryModel, TeacherModel
from django.contrib.auth.models import User


class CourseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModel
        fields = ['id', 'course_name', 'description', 'category', 'level', 'bullet_points', 'cover', 'created_at', 'updated_at']


class ClassModelSerializer(serializers.ModelSerializer):
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseModel.objects.all(),
        source='course'
    )
    
    class Meta:
        model = ClassModel
        fields = ['id', 'class_name', 'description', 'course_id', 'bullet_points', 'cover', 'created_at', 'updated_at']


class LayoutModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LayoutModel
        fields = ['id', 'class_model', 'title', 'instructions', 'cover', 'audio', 'audio_script']


class MultipleChoiceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceModel
        fields = ['id', 'tittle', 'instructions', 'script', 'question', 'cover', 'audio', 'stats']


class TrueOrFalseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrueOrFalseModel
        fields = ['id', 'layout', 'instructions', 'questions', 'order']


class OrderingTaskModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderingTaskModel
        fields = ['id', 'layout', 'instructions', 'items', 'order']


class CategoriesTaskModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriesTaskModel
        fields = ['id', 'layout', 'instructions', 'categories', 'order']


class FillInTheGapsTaskModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FillInTheGapsTaskModel
        fields = ['id', 'layout', 'instructions', 'text_with_gaps', 'keywords', 'order']


class VideoLayoutModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoLayoutModel
        fields = ['id', 'title', 'instructions', 'video_file', 'script', 'created_at', 'updated_at']


class TextBlockLayoutModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextBlockLayoutModel
        fields = ['id', 'title', 'instructions', 'content', 'created_at', 'updated_at']


class MediaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaModel
        fields = ['id', 'media_type', 'file', 'description', 'created_at', 'updated_at']


class MultimediaBlockVideoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultimediaBlockVideoModel
        fields = ['id', 'video', 'script', 'cover']


class ClassContentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassContentModel
        fields = ['id', 'class_id', 'content_type', 'tittle', 
                  'instructions', 'content_details', 'multimedia', 
                  'image', 'video', 'video_transcription', 
                  'embed_video', 'audio', 'audio_transcription', 
                  'pdf', 'order', 'stats', 
                  'created_at', 'updated_at']

    def validate_content_details(self, value):
        """
        Validar que content_details sea un diccionario válido con la estructura correcta
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("content_details debe ser un objeto JSON")
        
        if 'images' in value and not isinstance(value['images'], list):
            raise serializers.ValidationError("El campo 'images' debe ser una lista")
        
        return value

    def create(self, validated_data):
        """
        Crear una instancia de ClassContentModel con los datos validados
        """
        return ClassContentModel.objects.create(**validated_data)


class ScenarioModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioModel
        fields = [
            'id', 'class_id', 'cover', 'name', 'description',
            'goals', 'objectives', 'student_information',
            'role_polly', 'role_student', 'conversation_starter',
            'vocabulary', 'key_expressions', 'end_conversation',
            'end_conversation_saying', 'feedback', 'scoring',
            'additional_info', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        # Eliminar la validación JSON de los campos TextField
        return data


class FormattedTextModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormattedTextModel
        fields = [
            'id', 'class_id', 'title', 'content', 
            'instructions', 'order', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        # Validación adicional
        if not data.get('content'):
            raise serializers.ValidationError({
                'content': 'El contenido no puede estar vacío'
            })
        
        if not data.get('class_id'):
            raise serializers.ValidationError({
                'class_id': 'La clase es requerida'
            })

        return data


class StudentModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)  # Para crear
    email = serializers.EmailField(write_only=True)    # Para crear
    user_username = serializers.CharField(source='user.username', read_only=True)  # Para listar
    user_email = serializers.EmailField(source='user.email', read_only=True)      # Para listar

    class Meta:
        model = StudentModel
        fields = ['id', 'username', 'email', 'user_username', 'user_email', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Extraer username y email de los datos validados
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        
        try:
            # Crear el usuario
            user = User.objects.create_user(
                username=username,
                email=email
            )
            
            # Crear y retornar el estudiante
            student = StudentModel.objects.create(user=user, **validated_data)
            return student
        except Exception as e:
            raise serializers.ValidationError(f"Error al crear el estudiante: {str(e)}")

class TeacherModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)  # Para crear
    email = serializers.EmailField(write_only=True)    # Para crear
    user_username = serializers.CharField(source='user.username', read_only=True)  # Para listar
    user_email = serializers.EmailField(source='user.email', read_only=True)      # Para listar

    class Meta:
        model = TeacherModel
        fields = ['id', 'username', 'email', 'user_username', 'user_email', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Extraer username y email de los datos validados
        username = validated_data.pop('username')
        email = validated_data.pop('email')

        try:
            # Crear el usuario
            user = User.objects.create_user(
                username=username,
                email=email
            )
            
            # Crear y retornar el profesor
            teacher = TeacherModel.objects.create(user=user, **validated_data)
            return teacher
        except Exception as e:
            raise serializers.ValidationError(f"Error al registrar creador de contenido: {str(e)}")

class StudentNoteModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentNoteModel
        fields = ['id', 'student', 'class_model', 'title', 'content', 'note_type', 'tags', 'highlighted', 'color', 'related_url', 'related_content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        # Validar que el estudiante existe
        if not StudentModel.objects.filter(id=data['student'].id).exists():
            raise serializers.ValidationError("El estudiante especificado no existe")
        
        # Si se proporciona class_model, validar que existe
        if data.get('class_model') and not ClassModel.objects.filter(id=data['class_model'].id).exists():
            raise serializers.ValidationError("La clase especificada no existe")
            
        return data


class VocabularyEntryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VocabularyEntryModel
        fields = [
            'id', 'student', 'class_model', 'term', 'translation', 
            'context', 'notes', 'entry_type', 'tags', 'category',
            'proficiency_level', 'times_practiced', 'last_practiced',
            'next_review', 'audio_pronunciation', 'image',
            'is_favorite', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'times_practiced', 
                           'last_practiced', 'next_review']

    def validate(self, data):
        # Validar que el estudiante existe
        if not StudentModel.objects.filter(id=data['student'].id).exists():
            raise serializers.ValidationError("El estudiante especificado no existe")
        
        # Si se proporciona class_model, validar que existe
        if data.get('class_model') and not ClassModel.objects.filter(id=data['class_model'].id).exists():
            raise serializers.ValidationError("La clase especificada no existe")
            
        return data
