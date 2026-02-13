from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Payment, Subscription
from materials.models import Course, Lesson

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'username']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            username=validated_data.get('username', validated_data['email'])
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'username', 'city']


class SubscriptionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'user_email', 'course', 'course_title', 'created_at']
        read_only_fields = ['user', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежей"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'payment_date', 'course', 'course_title',
            'lesson', 'lesson_title', 'amount', 'payment_method'
        ]
        read_only_fields = ['user', 'payment_date']


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя с историей платежей"""
    payment_history = serializers.SerializerMethodField()
    subscriptions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'city', 
                  'payment_history', 'subscriptions']
    
    def get_payment_history(self, obj):
        payments = obj.payments.all()[:10]
        return PaymentSerializer(payments, many=True).data
    
    def get_subscriptions(self, obj):
        subs = obj.subscriptions.all()
        return SubscriptionSerializer(subs, many=True).data
