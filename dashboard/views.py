from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.http import HttpResponse
from .serializers import CourseModelSerializer, ClassModelSerializer, LayoutModelSerializer, MultipleChoiceModelSerializer,  TrueOrFalseModelSerializer, OrderingTaskModelSerializer, CategoriesTaskModelSerializer, FillInTheGapsTaskModelSerializer
from .models import CourseModel, ClassModel, LayoutModel, MultipleChoiceModel,TrueOrFalseModel, OrderingTaskModel, CategoriesTaskModel, FillInTheGapsTaskModel
from django.core.exceptions import ValidationError
from django.conf import settings
# Create your views here.

    ## API CRUD
class CourseView(viewsets.ModelViewSet):
    serializer_class = CourseModelSerializer
    queryset = CourseModel.objects.all()

class ClassModelViewSet(viewsets.ModelViewSet):
    queryset = ClassModel.objects.all()
    serializer_class = ClassModelSerializer
    #permission_classes = [IsAuthenticated]

    """
        def perform_create(self, serializer):
            serializer.save(course=self.get_object())
    """

class LayoutModelViewSet(viewsets.ModelViewSet):
    queryset = LayoutModel.objects.all()
    serializer_class = LayoutModelSerializer
    #permission_classes = [IsAuthenticated]

class MultipleChoiceModelViewSet(viewsets.ModelViewSet):
    queryset = MultipleChoiceModel.objects.all()
    serializer_class = MultipleChoiceModelSerializer
    #permission_classes = [IsAuthenticated]

class TrueOrFalseModelViewSet(viewsets.ModelViewSet):
    queryset = TrueOrFalseModel.objects.all()
    serializer_class = TrueOrFalseModelSerializer
    #permission_classes = [IsAuthenticated]

class OrderingTaskModelViewSet(viewsets.ModelViewSet):
    queryset = OrderingTaskModel.objects.all()
    serializer_class = OrderingTaskModelSerializer
    #permission_classes = [IsAuthenticated]

class CategoriesTaskModelViewSet(viewsets.ModelViewSet):
    queryset = CategoriesTaskModel.objects.all()
    serializer_class = CategoriesTaskModelSerializer
    #permission_classes = [IsAuthenticated]

class FillInTheGapsTaskModelViewSet(viewsets.ModelViewSet):
    queryset = FillInTheGapsTaskModel.objects.all()
    serializer_class = FillInTheGapsTaskModelSerializer
    #permission_classes = [IsAuthenticated]
