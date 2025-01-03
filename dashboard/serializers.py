from rest_framework import serializers
from .models import CourseModel, ClassModel, LayoutModel, MultipleChoiceModel, TrueOrFalseModel, OrderingTaskModel, CategoriesTaskModel, FillInTheGapsTaskModel, VideoLayoutModel, TextBlockLayoutModel, MediaModel, MultimediaBlockVideoModel, ClassContentModel, ScenarioModel, FormattedTextModel

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
                 'content_details', 'multimedia', 'order', 'stats', 
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
            'id', 'class_model', 'name', 'type', 'location', 'description',
            'goals', 'vocabulary', 'key_expressions', 'additional_info_objective',
            'limitations_student', 'role_student', 'role_polly',
            'instructions_polly', 'limitations_polly', 'created_at', 'updated_at'
        ]


class FormattedTextModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormattedTextModel
        fields = [
            'id', 'class_model', 'title', 'content', 
            'instructions', 'order', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        # Validación adicional
        if not data.get('content'):
            raise serializers.ValidationError({
                'content': 'El contenido no puede estar vacío'
            })
        
        if not data.get('class_model'):
            raise serializers.ValidationError({
                'class_model': 'La clase es requerida'
            })

        return data
