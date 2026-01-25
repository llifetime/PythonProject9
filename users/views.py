from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import update_session_auth_hash
from .models import User
from .serializers import (
    UserSerializer, UserCreateSerializer,
    UserUpdateSerializer, PasswordChangeSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями"""

    queryset = User.objects.all().order_by('email')
    permission_classes = [permissions.AllowAny]  # Временно открыт доступ для всех

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return PasswordChangeSerializer
        return UserSerializer

    def get_permissions(self):
        """Настройка разрешений для разных действий"""
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'list':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], url_path='change-password')
    def change_password(self, request, pk=None):
        """Изменение пароля пользователя"""
        user = self.get_object()
        serializer = PasswordChangeSerializer(data=request.data)

        if serializer.is_valid():
            # Проверка старого пароля
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Установка нового пароля
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            # Обновление сессии, если пользователь меняет свой пароль
            if user == request.user:
                update_session_auth_hash(request, user)

            return Response({"detail": "Password changed successfully."})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        """Получение профиля текущего пользователя"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)