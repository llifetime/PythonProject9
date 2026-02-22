from django.db import models
from django.conf import settings


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название курса')
    description = models.TextField(verbose_name='Описание курса', blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Цена курса'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Владелец',
        related_name='courses'
    )
    # Поля для Stripe
    stripe_product_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID продукта в Stripe',
        help_text='Идентификатор продукта в Stripe, создается автоматически'
    )
    stripe_price_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID цены в Stripe',
        help_text='Идентификатор цены в Stripe, создается автоматически'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_stripe_price_in_cents(self):
        """
        Возвращает цену в центах для Stripe API
        """
        return int(self.price * 100)


class Lesson(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название урока')
    description = models.TextField(verbose_name='Описание урока', blank=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Курс'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Владелец',
        related_name='lessons'
    )
    content = models.TextField(verbose_name='Содержание урока', blank=True)
    video_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Ссылка на видео'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['course', 'order']

    def __str__(self):
        if self.course:
            return f"{self.title} (Курс: {self.course.title})"
        return self.title


class Payment(models.Model):
    """
    Модель для отслеживания платежей через Stripe
    """

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Ожидает оплаты'
        PAID = 'paid', 'Оплачен'
        FAILED = 'failed', 'Ошибка оплаты'
        REFUNDED = 'refunded', 'Возвращен'
        CANCELLED = 'cancelled', 'Отменен'

    class PaymentTypeChoices(models.TextChoices):
        ONE_TIME = 'one_time', 'Разовый платеж'
        SUBSCRIPTION = 'subscription', 'Подписка'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='materials_payments',
        verbose_name='Пользователь'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Курс'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма платежа'
    )
    currency = models.CharField(
        max_length=3,
        default='usd',
        verbose_name='Валюта'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        db_index=True,
        verbose_name='Статус'
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentTypeChoices.choices,
        default=PaymentTypeChoices.ONE_TIME,
        verbose_name='Тип платежа'
    )

    # Поля Stripe
    stripe_session_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name='ID сессии Stripe',
        help_text='Идентификатор сессии checkout в Stripe'
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        verbose_name='ID Payment Intent',
        help_text='Идентификатор платежного намерения в Stripe'
    )
    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID клиента Stripe',
        help_text='Идентификатор клиента в Stripe (если есть)'
    )
    stripe_invoice_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID инвойса Stripe',
        help_text='Идентификатор инвойса в Stripe (для подписок)'
    )
    stripe_subscription_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID подписки Stripe',
        help_text='Идентификатор подписки в Stripe'
    )

    # Дополнительная информация
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Метод оплаты',
        help_text='Например: card, apple_pay, google_pay'
    )
    last4 = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name='Последние 4 цифры карты'
    )
    receipt_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Ссылка на чек'
    )

    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата оплаты'
    )

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"Платеж {self.id}: {self.user.email if self.user else 'Аноним'} - {self.course.title} - {self.status}"

    def mark_as_paid(self):
        """
        Отметить платеж как оплаченный
        """
        from django.utils import timezone
        self.status = self.StatusChoices.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at', 'updated_at'])

    def mark_as_failed(self):
        """
        Отметить платеж как неудачный
        """
        self.status = self.StatusChoices.FAILED
        self.save(update_fields=['status', 'updated_at'])

    def mark_as_refunded(self):
        """
        Отметить платеж как возвращенный
        """
        self.status = self.StatusChoices.REFUNDED
        self.save(update_fields=['status', 'updated_at'])


class UserCourseAccess(models.Model):
    """
    Модель для отслеживания доступа пользователя к курсу после оплаты
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_access',
        verbose_name='Пользователь'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='user_access',
        verbose_name='Курс'
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='access',
        verbose_name='Платеж'
    )
    access_granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата предоставления доступа'
    )
    access_expires_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата истечения доступа'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Доступ активен'
    )

    class Meta:
        verbose_name = 'Доступ к курсу'
        verbose_name_plural = 'Доступы к курсам'
        unique_together = ['user', 'course']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.course.title} - {'Активен' if self.is_active else 'Неактивен'}"