# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from .models import Payment

User = get_user_model()


# Сериализатор для регистрации
class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2',
                  'first_name', 'last_name', 'phone', 'city')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Пароли не совпадают"}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


# Сериализатор для пользователя
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'phone', 'city', 'avatar',
                  'is_staff', 'is_active', 'date_joined')
        read_only_fields = ('is_staff', 'is_active', 'date_joined')


# Сериализатор для публичного профиля
class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'city', 'avatar']
        read_only_fields = fields


# Сериализатор для истории платежей
class PaymentHistorySerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='paid_course.title', read_only=True)
    lesson_title = serializers.CharField(source='paid_lesson.title', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'payment_date', 'amount', 'payment_method',
                  'course_title', 'lesson_title']


# Сериализатор для профиля с историей платежей
class UserProfileSerializer(serializers.ModelSerializer):
    payment_history = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'phone', 'city', 'avatar', 'payment_history')
        read_only_fields = ('id', 'email', 'payment_history')

    def get_payment_history(self, obj):
        # История платежей видна только для своего профиля
        request = self.context.get('request')
        if request and request.user == obj:
            payments = obj.payments.all()
            return PaymentHistorySerializer(payments, many=True).data
        return []


# Сериализатор для платежей
class PaymentSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    course_title = serializers.CharField(source='paid_course.title', read_only=True)
    lesson_title = serializers.CharField(source='paid_lesson.title', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_info', 'payment_date',
            'paid_course', 'paid_lesson', 'course_title', 'lesson_title',
            'amount', 'payment_method'
        ]
        read_only_fields = ['user', 'user_info', 'payment_date']