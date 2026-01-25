from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока"""

    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'description', 'preview', 'video_url', 'created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса"""

    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons', 'lessons_count', 'created_at', 'updated_at']

    def get_lessons_count(self, obj):
        """Получение количества уроков в курсе"""
        return obj.lessons.count()
