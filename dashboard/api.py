from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import CourseModel, ClassModel, LayoutModel
from .serializers import CourseModelSerializer, ClassModelSerializer, LayoutModelSerializer
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
