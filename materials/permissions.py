# materials/permissions.py
from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверка, является ли пользователь модератором"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='Модераторы').exists()


class IsOwnerOrModerator(permissions.BasePermission):
    """Разрешает доступ владельцу или модератору"""

    def has_object_permission(self, request, view, obj):
        # Модераторы могут читать все, но не могут удалять
        if request.user.groups.filter(name='Модераторы').exists():
            return request.method in permissions.SAFE_METHODS  # GET, HEAD, OPTIONS

        # Владельцы могут все со своими объектами
        return obj.owner == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешает полный доступ владельцу, остальным только чтение"""

    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Запись только владельцу
        return obj.owner == request.user