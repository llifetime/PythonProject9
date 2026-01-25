from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения данных пользователя"""

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone', 'city', 'avatar', 'is_staff',
            'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = [
            'id', 'is_staff', 'is_active',
            'date_joined', 'last_login'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password2',
            'first_name', 'last_name', 'phone', 'city', 'avatar'
        ]

    def validate(self, attrs):
        """Проверка совпадения паролей"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """Создание пользователя"""
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления пользователя"""

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone', 'city', 'avatar'
        ]
        read_only_fields = ['id', 'email']  # email нельзя менять


class PasswordChangeSerializer(serializers.Serializer):
    """Сериализатор для изменения пароля"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        """Проверка совпадения новых паролей"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "New password fields didn't match."})
        return attrs