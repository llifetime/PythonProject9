from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Менеджер для модели пользователя с email в качестве идентификатора"""

    def create_user(self, email, password=None, **extra_fields):
        """Создает и возвращает пользователя с email, паролем"""
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создает и возвращает суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя с email для авторизации"""

    # Отключаем поле username
    username = None

    # Поле email становится основным для авторизации
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. Used for login.')
    )

    # Дополнительные поля
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        help_text=_('Phone number in international format')
    )

    city = models.CharField(
        _('city'),
        max_length=100,
        blank=True,
        help_text=_('City of residence')
    )

    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text=_('User profile picture')
    )

    # Переопределяем поле для авторизации
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Убираем email из REQUIRED_FIELDS так как он уже в USERNAME_FIELD

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"

    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() if full_name.strip() else self.email

    def get_short_name(self):
        """Возвращает короткое имя пользователя"""
        return self.first_name if self.first_name else self.email

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
        ]