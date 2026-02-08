# users/views.py
from rest_framework import viewsets, generics, permissions, status, filters, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from .models import Payment
from .serializers import (
    UserRegisterSerializer,
    UserSerializer,
    UserProfileSerializer,
    PaymentSerializer,
    PaymentHistorySerializer
)
from .filters import PaymentFilter
from .permissions import IsOwnerOrReadOnly

User = get_user_model()


# Сериализатор для публичного профиля (определяем здесь, а не в serializers.py)
class PublicUserSerializer(serializers.ModelSerializer):
    """Сериализатор для публичного профиля (без приватных данных)"""

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'city', 'avatar']
        read_only_fields = fields


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Разрешаем регистрацию без авторизации
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['retrieve', 'list']:
            # Чтение профилей доступно всем авторизованным
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Изменять и удалять можно только свой профиль
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        elif self.action == 'public_profile':
            # Публичный профиль доступен всем
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        elif self.action == 'public_profile':
            return PublicUserSerializer
        return UserSerializer

    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        """Получение и обновление профиля текущего пользователя"""
        user = request.user
        if request.method == 'GET':
            serializer = UserProfileSerializer(user, context={'request': request})
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            serializer = UserProfileSerializer(
                user, data=request.data,
                partial=request.method == 'PATCH',
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def public_profile(self, request, pk=None):
        """Публичный профиль пользователя (для всех)"""
        user = self.get_object()
        serializer = PublicUserSerializer(user)
        return Response(serializer.data)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомный вью для получения JWT токена"""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(username=request.data.get('username'))
            response.data['user'] = UserSerializer(user).data
        return response


class RegisterView(generics.CreateAPIView):
    """Регистрация пользователя"""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Создаем JWT токены
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date', 'amount']
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Пользователи видят только свои платежи
        # Модераторы видят все (проверка будет в задании 3)
        if self.request.user.groups.filter(name='Модераторы').exists():
            return Payment.objects.all()
        return Payment.objects.filter(user=self.request.user)