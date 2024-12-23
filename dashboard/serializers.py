from rest_framework import serializers
from .models import CourseModel, ClassModel, LayoutModel, MultipleChoiceModel, TrueOrFalseModel, OrderingTaskModel, CategoriesTaskModel, FillInTheGapsTaskModel, VideoLayoutModel, TextBlockLayoutModel, MediaModel, MultimediaBlockVideoModel, ClassContentModel

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
        fields = ['id', 'class_id', 'content_type', 'tittle', 'instructions', 
                 'content_details', 'multimedia', 'order', 'stats', 
                 'created_at', 'updated_at', 'image', 'video', 'video_transcription', 'embed_video', 'audio', 'audio_transcription', 'pdf']

    def validate_content_details(self, value):
        if value is not None:
            if not isinstance(value, (dict, list)):
                raise serializers.ValidationError("El contenido debe ser un objeto o array JSON válido")
        return value

    def validate_multimedia(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise serializers.ValidationError("El campo multimedia debe ser una lista")
        return value
