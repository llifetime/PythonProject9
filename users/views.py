from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny

from .models import Payment, Subscription, User
from .serializers import (
    PaymentSerializer, UserProfileSerializer,
    UserSerializer, RegisterSerializer, SubscriptionSerializer
)
from .permissions import IsOwnerOrReadOnly

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]  # ← обязательно AllowAny
    serializer_class = RegisterSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_staff or self.request.user.groups.filter(name='Модераторы').exists():
                return Payment.objects.all()
            return Payment.objects.filter(user=self.request.user)
        return Payment.objects.none()


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.IsAuthenticated()]



class SubscriptionViewSet(GenericViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        """Подписка на курс"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            from materials.models import Course
            course = Course.objects.get(pk=pk)

            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                course=course
            )

            if created:
                return Response(
                    {"status": "subscribed", "message": "Вы успешно подписались на курс"},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"status": "already_subscribed", "message": "Вы уже подписаны на этот курс"},
                    status=status.HTTP_200_OK
                )
        except Course.DoesNotExist:
            return Response(
                {"error": "Курс не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='unsubscribe')
    def unsubscribe(self, request, pk=None):
        """Отписка от курса"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            from materials.models import Course
            course = Course.objects.get(pk=pk)

            deleted_count, _ = Subscription.objects.filter(
                user=request.user,
                course=course
            ).delete()

            if deleted_count > 0:
                return Response(
                    {"status": "unsubscribed", "message": "Вы успешно отписались от курса"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"status": "not_subscribed", "message": "Вы не были подписаны на этот курс"},
                    status=status.HTTP_200_OK
                )
        except Course.DoesNotExist:
            return Response(
                {"error": "Курс не найден"},
                status=status.HTTP_404_NOT_FOUND
            )