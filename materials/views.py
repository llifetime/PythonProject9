from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
import logging
from .models import Course, Lesson
from django.contrib.auth import get_user_model
from .paginators import CoursePaginator, LessonPaginator
from .serializers import (
    SimpleLessonSerializer,
    SimpleCourseSerializer,
    CourseCreateSerializer
)

logger = logging.getLogger(__name__)
User = get_user_model()


# Простые permissions (оставляем как есть)
class IsOwnerOrModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.groups.filter(name='Модераторы').exists():
            return request.method in permissions.SAFE_METHODS or request.method in ['PUT', 'PATCH']

        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False


class IsNotModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return not request.user.groups.filter(name='Модераторы').exists()


class IsOwnerOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.groups.filter(name='Модераторы').exists():
            return False

        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с курсами.
    """
    queryset = Course.objects.all()
    serializer_class = SimpleCourseSerializer
    pagination_class = CoursePaginator

    def get_serializer_class(self):
        if self.action == 'create':
            return CourseCreateSerializer
        return SimpleCourseSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]  # анонимный доступ к чтению
        elif self.action == 'create':
            # Для создания нужна аутентификация
            return [permissions.IsAuthenticated(), IsNotModerator()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsOwnerOrModerator()]
        elif self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsOwnerOnly()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Course.objects.none()

        if self.request.user.groups.filter(name='Модераторы').exists():
            return Course.objects.all()

        return Course.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        # Автоматически обновляем поле updated_at
        serializer.save(updated_at=timezone.now())


class LessonViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с уроками.
    """
    queryset = Lesson.objects.all()
    serializer_class = SimpleLessonSerializer
    pagination_class = LessonPaginator

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]  # анонимный доступ к чтению
        elif self.action == 'create':
            # Для создания нужна аутентификация
            return [permissions.IsAuthenticated(), IsNotModerator()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsOwnerOrModerator()]
        elif self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsOwnerOnly()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Lesson.objects.none()

        if self.request.user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        # Обновляем урок и его курс
        lesson = serializer.save(updated_at=timezone.now())
        # Обновляем время курса
        if lesson.course:
            lesson.course.save()  # автоматически обновит updated_at