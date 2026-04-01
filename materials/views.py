from rest_framework import permissions, viewsets
from rest_framework.permissions import BasePermission

from materials.models import Lesson, Course
from materials.paginators import CoursePaginator, LessonPaginator
from materials.serializers import (
    SimpleLessonSerializer,
    SimpleCourseSerializer,
    CourseCreateSerializer
)


class IsNotModerator(BasePermission):
    def has_permission(self, request, view):
        # Неавторизованные пользователи не могут создавать
        if not request.user.is_authenticated:
            return False
        return not request.user.groups.filter(name='Модераторы').exists()


class IsOwnerOrModerator(BasePermission):
    """Разрешение для владельца объекта или модератора"""

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Модераторы могут редактировать
        if request.user.groups.filter(name='Модераторы').exists():
            return request.method in permissions.SAFE_METHODS or request.method in ['PUT', 'PATCH']

        # Владелец может редактировать
        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False


class IsOwnerOnly(BasePermission):
    """Разрешение только для владельца объекта"""

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Модераторы не могут удалять
        if request.user.groups.filter(name='Модераторы').exists():
            return False

        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = SimpleCourseSerializer
    pagination_class = CoursePaginator

    def get_serializer_class(self):
        if self.action == 'create':
            return CourseCreateSerializer
        return SimpleCourseSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated(), IsNotModerator()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsOwnerOrModerator()]
        elif self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsOwnerOnly()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Для неаутентифицированных пользователей возвращаем все курсы (только для чтения)
        if not self.request.user.is_authenticated:
            return Course.objects.all()  # ← вернуть все для чтения

        if self.request.user.groups.filter(name='Модераторы').exists():
            return Course.objects.all()

        return Course.objects.filter(owner=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = SimpleLessonSerializer
    pagination_class = LessonPaginator

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated(), IsNotModerator()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsOwnerOrModerator()]
        elif self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsOwnerOnly()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Для всех запросов возвращаем все уроки
        # Права проверяются в permissions
        return Lesson.objects.all()