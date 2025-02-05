from rest_framework import serializers
from .models import CourseModel, ClassModel, LayoutModel, VideoLayoutModel, TextBlockLayoutModel, MediaModel, ClassContentModel, ScenarioModel, StudentModel, StudentNoteModel, VocabularyEntryModel, TeacherModel, StudentLoginRecord, StudentWordsModel
from django.contrib.auth.models import User


class CourseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModel
        fields = ['id', 'course_name', 'description', 'category', 'level', 'bullet_points', 'cover', 'publish', 'created_at', 'updated_at']


class ClassModelSerializer(serializers.ModelSerializer):
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseModel.objects.all(),
        source='course'
    )
    
    class Meta:
        model = ClassModel
        fields = ['id', 'class_name', 'description', 'course_id', 'bullet_points', 'cover', 'publish', 'created_at', 'updated_at']


class LayoutModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LayoutModel
        fields = ['id', 'class_model', 'tittle', 'instructions', 'cover', 'audio', 'audio_script']


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

    def to_representation(self, instance):
        """Personalizar la representación de la respuesta"""
        data = super().to_representation(instance)
        return {
            'id': data['id'],
            'tittle': data['tittle'],
            'instructions': data['instructions'],
            'content_type': data['content_type'],
            'class_id': data['class_id'],
            'order': data['order'],
            'content_details': data.get('content_details', {}),
            'created_at': data['created_at'],
            'updated_at': data['updated_at']
        }


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



class StudentModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = StudentModel
        fields = ['id', 'username', 'email', 'password', 'user_username', 
                 'user_email', 'profile_picture', 'courses', 'created_at', 'updated_at']

    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        profile_picture = validated_data.pop('profile_picture', None)

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            student = StudentModel.objects.create(
                user=user,
                profile_picture=profile_picture,
                **validated_data
            )
            return student
        except Exception as e:
            raise serializers.ValidationError(f"Error al registrar estudiante: {str(e)}")

class TeacherModelSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    profile_picture = serializers.ImageField(required=False)
    
    class Meta:
        model = TeacherModel
        fields = ['id', 'username', 'email', 'password', 'user_username', 
                 'user_email', 'profile_picture', 'created_at', 'updated_at']

    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        profile_picture = validated_data.pop('profile_picture', None)

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            teacher = TeacherModel.objects.create(
                user=user,
                profile_picture=profile_picture,
                **validated_data
            )
            return teacher
        except Exception as e:
            raise serializers.ValidationError(f"Error al registrar creador de contenido: {str(e)}")

class StudentNoteModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentNoteModel
        fields = ['id', 'student', 'class_id', 'title', 'content', 'note_type', 'tags', 'highlighted', 'color', 'related_url', 'related_content', 'created_at', 'updated_at']
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


class StudentLoginRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentLoginRecord
        fields = ['student', 'login_date']

    def create(self, validated_data):
        return StudentLoginRecord.objects.create(**validated_data)

class AskOpenAISerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField(read_only=True)

class TranscribeAudioSerializer(serializers.Serializer):
    audio_file = serializers.FileField()
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=['student', 'teacher'])

class SearchSerializer(serializers.Serializer):
    query = serializers.CharField()
    filter_type = serializers.ChoiceField(choices=['all', 'courses', 'classes', 'content'], required=False)

class TextToSpeechRequestSerializer(serializers.Serializer):
    texto = serializers.CharField(required=True)
    voz = serializers.CharField(required=False, default='alloy')

class StudentCoursesSerializer(serializers.Serializer):
    courses = CourseModelSerializer(many=True)
    progress = serializers.DictField()

class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user_type = serializers.CharField()

class TranscribeAudioResponseSerializer(serializers.Serializer):
    transcription = serializers.CharField()
    pronunciation_analysis = serializers.DictField()

class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()

class SuccessResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()
    data = serializers.DictField(required=False)

class GenericResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()

class TextToSpeechResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()
    audio_url = serializers.CharField()

class LogoutResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()

class UnifiedLogoutResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

class StudentWordsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentWordsModel
        fields = [
            'id', 'student', 'english_word', 'spanish_word', 
            'favorite', 'learned', 'audio', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        if not StudentModel.objects.filter(id=data['student'].id).exists():
            raise serializers.ValidationError("El estudiante especificado no existe")
        return data