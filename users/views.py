from rest_framework import viewsets, filters, permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment, User
from .permissions import IsOwnerOrReadOnly

# Временный простой сериализатор для избежания циклических зависимостей
from rest_framework import serializers

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'username']


class SimplePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'payment_date', 'course', 'lesson', 'amount', 'payment_method']
        read_only_fields = ['user', 'payment_date']


class RegisterView(generics.CreateAPIView):
    """Отдельный эндпоинт для регистрации"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        # Простой сериализатор для регистрации
        class RegisterSerializer(serializers.ModelSerializer):
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
                    username=validated_data.get('username', '')
                )
                return user
        
        return RegisterSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        return SimpleUserSerializer
    
    def get_permissions(self):
        # Убрать возможность создания через ViewSet
        if self.action in ['retrieve', 'list']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def public_profile(self, request):
        """Публичный профиль (если нужен)"""
        return Response({"message": "Public profile endpoint"})


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = SimplePaymentSerializer
    
    # Задание 4: Настройка фильтрации
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']
    
    def get_queryset(self):
        # Пользователи видят только свои платежи
        if self.request.user.is_authenticated:
            if self.request.user.is_staff or self.request.user.groups.filter(name='Модераторы').exists():
                return Payment.objects.all()
            return Payment.objects.filter(user=self.request.user)
        return Payment.objects.none()


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = SimpleUserSerializer
    
    def get_queryset(self):
        # Пользователь видит только свой профиль
        return User.objects.filter(id=self.request.user.id)
