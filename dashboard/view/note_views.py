from rest_framework import viewsets
from ..models import StudentNoteModel, VocabularyEntryModel
from ..serializers import StudentNoteModelSerializer, VocabularyEntryModelSerializer

class StudentNoteViewSet(viewsets.ModelViewSet):
    queryset = StudentNoteModel.objects.all()
    serializer_class = StudentNoteModelSerializer
    model_name = 'nota de estudiante'

class VocabularyEntryViewSet(viewsets.ModelViewSet):
    queryset = VocabularyEntryModel.objects.all()
    serializer_class = VocabularyEntryModelSerializer
    model_name = 'entrada de vocabulario' 