from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import Payment, Subscription, User  # ← Subscription добавлен
from .serializers import (
    PaymentSerializer, UserProfileSerializer,
    UserSerializer, RegisterSerializer, SubscriptionSerializer
)
from .permissions import IsOwnerOrReadOnly


class SubscriptionViewSet(GenericViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        """
        Возвращаем 401 для неавторизованных, 403 для авторизованных без прав
        """
        if not self.request.user.is_authenticated:
            return [permissions.IsAuthenticated()]  # вернет 401
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        """Подписка на курс"""
        # Проверка аутентификации
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
        # Проверка аутентификации
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