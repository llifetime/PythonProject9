from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .tasks import send_course_update_notification
import logging
from .models import Course, Lesson, Payment, UserCourseAccess
from .services.stripe_service import StripeService

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Lesson)
def notify_lesson_update(sender, instance, created, **kwargs):
    """
    Отправка уведомлений при обновлении урока
    """
    if not created and instance.course:  # Только при обновлении
        course = instance.course
        time_since_update = timezone.now() - course.updated_at
        if time_since_update >= timedelta(hours=4):
            # Запускаем задачу с указанием обновленного урока
            send_course_update_notification.delay(course.id, instance.id)
            logger.info(f"Задача на отправку уведомлений для урока {instance.id} курса {course.id} поставлена в очередь")

@receiver(post_save, sender=Course)
def notify_course_update(sender, instance, created, **kwargs):
    """
    Отправка уведомлений при обновлении курса
    """
    if not created:  # Только при обновлении, не при создании
        # Проверяем, прошло ли 4 часа с последнего обновления
        time_since_update = timezone.now() - instance.updated_at
        if time_since_update >= timedelta(hours=4):
            # Запускаем задачу асинхронно
            send_course_update_notification.delay(instance.id)
            logger.info(f"Задача на отправку уведомлений для курса {instance.id} поставлена в очередь")

@receiver(post_save, sender=Course)
def create_stripe_product(sender, instance, created, **kwargs):
    """
    Сигнал для автоматического создания продукта в Stripe при создании курса
    """
    if created and instance.price > 0:
        try:
            # Создаем продукт и цену в Stripe
            StripeService.create_product(instance)
            StripeService.create_price(instance)
            logger.info(f"Stripe product and price created for course {instance.id}")
        except Exception as e:
            logger.error(f"Failed to create Stripe product for course {instance.id}: {str(e)}")


@receiver(pre_save, sender=Course)
def update_stripe_price(sender, instance, **kwargs):
    """
    Сигнал для обновления цены в Stripe при изменении цены курса
    """
    if instance.pk:
        try:
            old_instance = Course.objects.get(pk=instance.pk)
            if old_instance.price != instance.price and instance.stripe_product_id:
                # Цена изменилась, создаем новую цену в Stripe
                StripeService.create_price(instance)
                logger.info(f"Stripe price updated for course {instance.id}")
        except Course.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Failed to update Stripe price for course {instance.id}: {str(e)}")


@receiver(post_save, sender=Payment)
def grant_course_access(sender, instance, created, **kwargs):
    """
    Сигнал для предоставления доступа к курсу после успешной оплаты
    """
    if instance.status == Payment.StatusChoices.PAID:
        access, created = UserCourseAccess.objects.get_or_create(
            user=instance.user,
            course=instance.course,
            defaults={
                'payment': instance,
                'is_active': True
            }
        )

        if not created and not access.is_active:
            access.is_active = True
            access.payment = instance
            access.save()

        logger.info(f"Course access granted to user {instance.user.id} for course {instance.course.id}")