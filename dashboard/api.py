from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import CourseModel, ClassModel, LayoutModel, MultipleChoiceModel, TrueOrFalseModel, OrderingTaskModel, CategoriesTaskModel, FillInTheGapsTaskModel
from .serializers import CourseModelSerializer, ClassModelSerializer, LayoutModelSerializer, MultipleChoiceModelSerializer, TrueOrFalseModelSerializer, OrderingTaskModelSerializer, CategoriesTaskModelSerializer, FillInTheGapsTaskModelSerializer

# ViewSet para CourseModel
class CourseModelViewSet(viewsets.ModelViewSet):
    queryset = CourseModel.objects.all()
    serializer_class = CourseModelSerializer
    permission_classes = [AllowAny]  # Permite el acceso sin restricciones

# ViewSet para LessonModel
class ClassModelViewSet(viewsets.ModelViewSet):
    queryset = ClassModel.objects.all()
    serializer_class = ClassModelSerializer
    permission_classes = [AllowAny]  # Permite el acceso sin restricciones

# ViewSet para LayoutModel
class LayoutModelViewSet(viewsets.ModelViewSet):
    queryset = LayoutModel.objects.all()
    serializer_class = LayoutModelSerializer
    permission_classes = [AllowAny]  # Permite el acceso sin restricciones

# ViewSet para MultipleChoiceModel
class MultipleChoiceModelViewSet(viewsets.ModelViewSet):
    queryset = MultipleChoiceModel.objects.all()
    serializer_class = MultipleChoiceModelSerializer
    permission_classes = [AllowAny]  # Permite el acceso sin restricciones

# ViewSet para TrueOrFalseModel
class TrueOrFalseModelViewSet(viewsets.ModelViewSet):
    queryset = TrueOrFalseModel.objects.all()
    serializer_class = TrueOrFalseModelSerializer
    permission_classes = [AllowAny]  # Permite el acceso sin restricciones

# ViewSet para OrderingTaskModel
class OrderingTaskModelViewSet(viewsets.ModelViewSet):
    queryset = OrderingTaskModel.objects.all()
    serializer_class = OrderingTaskModelSerializer
    permission_classes = [AllowAny]  # Permite el acceso sin restricciones

# ViewSet para CategoriesTaskModel
class CategoriesTaskModelViewSet(viewsets.ModelViewSet):
    queryset = CategoriesTaskModel.objects.all()
    serializer_class = CategoriesTaskModelSerializer
    permission_classes = [AllowAny]  # Permite el acceso sin restricciones

# ViewSet para FillInTheGapsTaskModel
class FillInTheGapsTaskModelViewSet(viewsets.ModelViewSet):
    queryset = FillInTheGapsTaskModel.objects.all()
    serializer_class = FillInTheGapsTaskModelSerializer
    permission_classes = [AllowAny]  # Permite el acceso sin restricciones
