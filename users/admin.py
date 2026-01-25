from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ-панель для пользователей"""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'phone', 'city', 'avatar')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'city'),
        }),
    )

    list_display = ('email', 'first_name', 'last_name', 'phone', 'city', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'city')
    search_fields = ('email', 'first_name', 'last_name', 'phone', 'city')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined')

    # Убираем поле username из формы
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'username' in form.base_fields:
            del form.base_fields['username']
        return form