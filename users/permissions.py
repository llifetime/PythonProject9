from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешает редактирование только владельцу, чтение - всем авторизованным"""
    
    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение всем авторизованным
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Редактирование только владельцу
        return obj == request.user
