from rest_framework import serializers
from .models import CourseModel, ClassModel, LayoutModel, MultipleChoiceModel, TrueOrFalseModel, OrderingTaskModel, CategoriesTaskModel, FillInTheGapsTaskModel

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
        fields = ['id', 'title', 'instructions', 'cover', 'audio', 'audio_script']


class MultipleChoiceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceModel
        fields = ['id', 'layout', 'instructions', 'question', 'answers', 'order']


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
