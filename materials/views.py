from rest_framework import viewsets, permissions
from .models import Course, Lesson
from django.contrib.auth import get_user_model
from .paginators import CoursePaginator, LessonPaginator

User = get_user_model()


# Простые сериализаторы для избежания зависимостей
from rest_framework import serializers

class SimpleLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class SimpleCourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = SimpleLessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'lessons_count', 'lessons', 'created_at', 'updated_at', 'owner']
        read_only_fields = ['owner']
    
    def get_lessons_count(self, obj):
        return obj.lessons.count()


# Простые permissions
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
    queryset = Course.objects.all()
    serializer_class = SimpleCourseSerializer
    pagination_class = CoursePaginator
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsNotModerator()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsOwnerOrModerator()]
        elif self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsOwnerOnly()]
        elif self.action in ['retrieve', 'list']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Course.objects.none()
        
        if self.request.user.groups.filter(name='Модераторы').exists():
            return Course.objects.all()
        
        return Course.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = SimpleLessonSerializer
    pagination_class = LessonPaginator
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsNotModerator()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsOwnerOrModerator()]
        elif self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsOwnerOnly()]
        elif self.action in ['retrieve', 'list']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Lesson.objects.none()
        
        if self.request.user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        
        return Lesson.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
