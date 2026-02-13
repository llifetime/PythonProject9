from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Payment, Subscription

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class PaymentSerializer(serializers.ModelSerializer):
    # Для чтения используем SerializerMethodField
    course = serializers.SerializerMethodField(read_only=True)
    lesson = serializers.SerializerMethodField(read_only=True)
    
    # Для записи используем PrimaryKeyRelatedField
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Установим в __init__
        source='course',
        write_only=True,
        required=False,
        allow_null=True
    )
    lesson_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Установим в __init__
        source='lesson',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'payment_date', 'course', 'lesson',
            'course_id', 'lesson_id', 'amount', 'payment_method'
        ]
        read_only_fields = ['user', 'payment_date']
    
    def get_course(self, obj):
        if obj.course:
            # Ленивый импорт
            from materials.serializers import CourseSerializer
            return CourseSerializer(obj.course).data
        return None
    
    def get_lesson(self, obj):
        if obj.lesson:
            # Ленивый импорт
            from materials.serializers import LessonSerializer
            return LessonSerializer(obj.lesson).data
        return None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем queryset после импорта моделей
        try:
            from materials.models import Course, Lesson
            self.fields['course_id'].queryset = Course.objects.all()
            self.fields['lesson_id'].queryset = Lesson.objects.all()
        except ImportError:
            # Если модели еще не существуют (при миграциях)
            self.fields['course_id'].queryset = None
            self.fields['lesson_id'].queryset = None


class UserProfileSerializer(serializers.ModelSerializer):
    # Дополнительное задание: История платежей пользователя
    payment_history = PaymentSerializer(many=True, read_only=True, source='payments')
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'payment_history']


# Добавляем в users/serializers.py
class SubscriptionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'user_email', 'course', 'course_title', 'created_at']
        read_only_fields = ['user', 'created_at']