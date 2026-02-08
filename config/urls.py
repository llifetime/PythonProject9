from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Импорты из приложений
from users.views import (
    PaymentViewSet, 
    UserProfileViewSet, 
    UserViewSet,
    RegisterView
)
from materials.views import CourseViewSet, LessonViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'users', UserViewSet, basename='users')
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'lessons', LessonViewSet, basename='lessons')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/register/', RegisterView.as_view(), name='register'),
    path('api-auth/', include('rest_framework.urls')),
]
