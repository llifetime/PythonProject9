# Создайте новый файл users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Кастомная модель пользователя"""
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Аватар")

    # Используем email для входа, но оставляем username для совместимости
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # Django требует username для createsuperuser

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счет"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments", verbose_name="Пользователь")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    paid_course = models.ForeignKey("materials.Course", on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name="Оплаченный курс")
    paid_lesson = models.ForeignKey("materials.Lesson", on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name="Оплаченный урок")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, verbose_name="Способ оплаты")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Платеж {self.user.email} - {self.amount}"