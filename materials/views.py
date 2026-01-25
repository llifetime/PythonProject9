from rest_framework import viewsets, generics, permissions
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для управления курсами"""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]  # Временно открыт доступ для всех


class LessonListCreateView(generics.ListCreateAPIView):
    """Представление для получения списка уроков и создания нового урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.AllowAny]  # Временно открыт доступ для всех


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Представление для получения, обновления и удаления урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.AllowAny]  # Временно открыт доступ для всех
