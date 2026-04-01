from django.db import models
from django.conf import settings  # ← это правильный импорт
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Кастомная модель пользователя"""
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    city = models.CharField(max_length=100, blank=True, verbose_name='Город')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']
    
    def __str__(self):
        return self.email

PAYMENT_METHOD_CHOICES = [
    ('card', 'Банковская карта'),
    ('cash', 'Наличные'),
    ('transfer', 'Банковский перевод'),
    ('other', 'Другое'),
]

class Payment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'  # ← добавьте это
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='users_payments',
        verbose_name='Пользователь'
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата оплаты'
    )
    course = models.ForeignKey(
        'materials.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Оплаченный курс'
    )
    lesson = models.ForeignKey(
        'materials.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Оплаченный урок'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма оплаты'
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Способ оплаты'
    )
    
    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Платеж {self.user.email} - {self.amount}"


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    course = models.ForeignKey(
        'materials.Course',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"
