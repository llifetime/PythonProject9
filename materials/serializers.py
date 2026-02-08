# materials/serializers.py
from rest_framework import serializers
from .models import Course, Lesson
from users.serializers import UserSerializer


class LessonSerializer(serializers.ModelSerializer):
    owner_info = UserSerializer(source='owner', read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'order',
                  'course', 'owner', 'owner_info', 'created_at']
        read_only_fields = ['owner', 'owner_info']


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    owner_info = UserSerializer(source='owner', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'price',
                  'lessons_count', 'owner', 'owner_info', 'created_at']
        read_only_fields = ['owner', 'owner_info']

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    owner_info = UserSerializer(source='owner', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'price',
                  'lessons_count', 'lessons', 'owner', 'owner_info', 'created_at']
        read_only_fields = ['owner', 'owner_info']

    def get_lessons_count(self, obj):
        return obj.lessons.count()