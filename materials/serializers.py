# materials/serializers.py
from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_url, YouTubeURLValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        # Использование класса-валидатора
        validators = [YouTubeURLValidator(field='video_url')]

    # Или использование функции-валидатора для конкретного поля
    video_url = serializers.URLField(
        validators=[validate_youtube_url],
        required=False,
        allow_blank=True,
        allow_null=True
    )


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'lessons_count', 'lessons',
                  'created_at', 'updated_at', 'owner', 'price', 'is_subscribed']
        read_only_fields = ['owner']

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscriptions.filter(user=request.user).exists()
        return False