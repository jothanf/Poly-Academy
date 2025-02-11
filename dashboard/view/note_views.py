from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models import StudentNoteModel, VocabularyEntryModel, StudentWordsModel, StudentModel
from ..serializers import StudentNoteModelSerializer, VocabularyEntryModelSerializer, StudentWordsModelSerializer
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from ..IA.openAI import AIService
import os
import uuid


class StudentNoteViewSet(viewsets.ModelViewSet):
    queryset = StudentNoteModel.objects.all()
    serializer_class = StudentNoteModelSerializer
    permission_classes = [IsAuthenticated]
    model_name = 'nota de estudiante'

    def get_queryset(self):
        # Filtrar notas por estudiante
        return self.queryset.filter(student=self.request.user.student)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            print(f"List Notes: {serializer.data}")  # Debug
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            print(f"Error en list_note: {str(e)}")  # Debug
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            print(f"Retrieve Note: {serializer.data}")  # Debug
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            print(f"Error en retrieve_note: {str(e)}")  # Debug
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            print(f"Updating Note ID: {instance.id}")  # Debug
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            print(f"Validated Data: {serializer.validated_data}")  # Debug
            self.perform_update(serializer)
            print(f"Updated Data: {serializer.data}")  # Debug
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            print(f"Error en update_note: {str(e)}")  # Debug
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            print(f"Deleted Note ID: {instance.id}")  # Debug
            return Response({
                'status': 'success',
                'message': 'Nota eliminada exitosamente'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error en delete_note: {str(e)}")  # Debug
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_name='by-class', url_path='by-class')
    def by_class(self, request):
        """Filtra las notas por clase específica"""
        try:
            class_id = request.query_params.get('class_id')
            if not class_id:
                return Response({
                    'status': 'error',
                    'message': 'Se requiere class_id'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            notes = self.get_queryset().filter(class_id=class_id)
            serializer = self.get_serializer(notes, many=True)
            print(f"Notes by Class {class_id}: {serializer.data}")  # Debug
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            print(f"Error en by_class: {str(e)}")  # Debug
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VocabularyEntryViewSet(viewsets.ModelViewSet):
    queryset = VocabularyEntryModel.objects.all()
    serializer_class = VocabularyEntryModelSerializer
    permission_classes = [IsAuthenticated]
    model_name = 'entrada de vocabulario'

    def get_queryset(self):
        # Filtrar vocabulario por estudiante
        return self.queryset.filter(student=self.request.user.student)

    def perform_create(self, serializer):
        # Asignar automáticamente el estudiante actual
        serializer.save(student=self.request.user.student)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            print(f"List Vocabulary: {serializer.data}")  # Debug
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            print(f"Error en list_vocabulary: {str(e)}")  # Debug
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            print(f"Retrieve Vocabulary: {serializer.data}")  # Debug
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            print(f"Error en retrieve_vocabulary: {str(e)}")  # Debug
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            print(f"Updating Vocabulary ID: {instance.id}")  # Debug
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            print(f"Validated Data: {serializer.validated_data}")  # Debug
            self.perform_update(serializer)
            print(f"Updated Vocabulary: {serializer.data}")  # Debug
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            print(f"Error en update_vocabulary: {str(e)}")  # Debug
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            print(f"Deleted Vocabulary ID: {instance.id}")  # Debug
            return Response({
                'status': 'success',
                'message': 'Entrada de vocabulario eliminada exitosamente'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error en delete_vocabulary: {str(e)}")  # Debug
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_name='toggle-favorite', url_path='toggle-favorite')
    def toggle_favorite(self, request, pk=None):
        """Alterna el estado de favorito de una entrada de vocabulario"""
        try:
            entry = self.get_object()
            entry.is_favorite = not entry.is_favorite
            entry.save()
            serializer = self.get_serializer(entry)
            print(f"Toggle favorite for entry ID {pk}: {entry.is_favorite}")  # Debug
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            print(f"Error en toggle_favorite: {str(e)}")  # Debug
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_name='favorites', url_path='favorites')
    def favorites(self, request):
        """Obtiene solo las entradas favoritas"""
        try:
            queryset = self.get_queryset().filter(is_favorite=True)
            serializer = self.get_serializer(queryset, many=True)
            print(f"Favorites: {serializer.data}")  # Debug
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            print(f"Error en favorites: {str(e)}")  # Debug
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_name='by-class', url_path='by-class')
    def by_class(self, request):
        """Filtra las entradas por clase específica"""
        try:
            class_id = request.query_params.get('class_id')
            if not class_id:
                return Response({
                    'status': 'error',
                    'message': 'Se requiere class_id'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            queryset = self.get_queryset().filter(class_model=class_id)
            serializer = self.get_serializer(queryset, many=True)
            print(f"Vocabulary by Class {class_id}: {serializer.data}")  # Debug
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            print(f"Error en by_class_vocabulary: {str(e)}")  # Debug
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentWordsViewSet(viewsets.ModelViewSet):
    serializer_class = StudentWordsModelSerializer
    permission_classes = [IsAuthenticated]
    model_name = 'palabra de estudiante'

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        return StudentWordsModel.objects.filter(student_id=student_id)

    def perform_create(self, serializer):
        try:
            student_id = self.kwargs['student_id']
            student = StudentModel.objects.get(user=self.request.user)
            
            if student.id != int(student_id):
                raise serializers.ValidationError("No tienes permiso para crear palabras para este estudiante")

            # Obtener las palabras del request
            english_word = serializer.validated_data.get('english_word')
            spanish_word = serializer.validated_data.get('spanish_word')

            ai_service = AIService()

            # Si falta alguna traducción, usar OpenAI para obtenerla
            if english_word and not spanish_word:
                spanish_word = ai_service.translate_to_spanish(english_word)
                serializer.validated_data['spanish_word'] = spanish_word
            elif spanish_word and not english_word:
                prompt = f"Translate this Spanish text to English: {spanish_word}"
                english_word = ai_service.chat_with_gpt(prompt)
                serializer.validated_data['english_word'] = english_word

            # Generar el audio para la palabra en inglés
            if english_word:
                # Crear el directorio temporal si no existe
                audio_dir = 'media/words_audio'
                os.makedirs(audio_dir, exist_ok=True)
                
                # Generar un nombre único para el archivo
                file_uuid = uuid.uuid4()
                output_file = f"{audio_dir}/word_{file_uuid}.mp3"
                
                # Generar el audio
                audio_file = ai_service.text_to_speech(english_word, voice='alloy', output_file=output_file)
                
                if audio_file:
                    # Asignar el archivo de audio al modelo
                    serializer.validated_data['audio'] = f"words_audio/word_{file_uuid}.mp3"

            serializer.save(student=student)
            
        except StudentModel.DoesNotExist:
            raise serializers.ValidationError("Estudiante no encontrado")
        except Exception as e:
            print(f"Error en perform_create: {str(e)}")
            raise serializers.ValidationError(f"Error al procesar la palabra: {str(e)}")

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                'status': 'success',
                'message': 'Palabra eliminada exitosamente'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        try:
            word = self.get_object()
            word.favorite = not word.favorite
            word.save()
            serializer = self.get_serializer(word)
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def toggle_learned(self, request, pk=None):
        try:
            word = self.get_object()
            word.learned = not word.learned
            word.save()
            serializer = self.get_serializer(word)
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        try:
            queryset = self.get_queryset().filter(favorite=True)
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def learned(self, request):
        try:
            queryset = self.get_queryset().filter(learned=True)
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 