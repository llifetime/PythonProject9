from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from .models import Subscription, User
from .serializers import RegisterSerializer, SubscriptionSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class SubscriptionViewSet(GenericViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        if not self.request.user.is_authenticated:
            return [permissions.IsAuthenticated()]
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