# materials/models.py
from django.db import models
from django.conf import settings


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название курса')
    description = models.TextField(verbose_name='Описание', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Цена')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name='Владелец'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']
        permissions = [
            ('can_change_description', 'Может менять описание'),
            ('can_change_category', 'Может менять категорию'),
        ]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Курс'
    )
    title = models.CharField(max_length=255, verbose_name='Название урока')
    description = models.TextField(verbose_name='Описание', blank=True)
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lessons',
        verbose_name='Владелец'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"