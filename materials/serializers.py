from rest_framework import serializers
from .models import Course, Lesson, Payment, UserCourseAccess


class SimpleLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'content', 'video_url', 'order', 'course', 'owner', 'created_at',
                  'updated_at']
        read_only_fields = ['owner']


class SimpleCourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = SimpleLessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'price', 'lessons_count', 'lessons', 'created_at', 'updated_at',
                  'owner']
        read_only_fields = ['owner']

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price']

    def validate_title(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Название курса должно содержать минимум 3 символа")
        return value


class PaymentCreateSerializer(serializers.Serializer):
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()


class PaymentStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    course_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    currency = serializers.CharField(required=False)
    payment_id = serializers.IntegerField(required=False)
    has_access = serializers.BooleanField(required=False)


class PaymentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'course', 'course_title', 'amount', 'status', 'created_at']