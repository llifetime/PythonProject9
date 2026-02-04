# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Payment
from materials.serializers import CourseSerializer, LessonSerializer

User = get_user_model()


# Сериализатор для платежей
class PaymentSerializer(serializers.ModelSerializer):
    course_info = CourseSerializer(source='paid_course', read_only=True)
    lesson_info = LessonSerializer(source='paid_lesson', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'payment_date', 'paid_course', 'paid_lesson',
            'course_info', 'lesson_info', 'amount', 'payment_method'
        ]
        read_only_fields = ['user', 'payment_date']


# Сериализатор для истории платежей в профиле
class PaymentHistorySerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='paid_course.title', read_only=True)
    lesson_title = serializers.CharField(source='paid_lesson.title', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'payment_date', 'amount', 'payment_method',
            'course_title', 'lesson_title'
        ]


# Сериализатор для профиля пользователя
class UserProfileSerializer(serializers.ModelSerializer):
    payment_history = PaymentHistorySerializer(many=True, read_only=True, source='payments')

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone', 'city', 'payment_history'
        ]
        read_only_fields = ['id', 'email', 'payment_history']