# materials/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging
from .models import Course, Lesson, UserCourseAccess

logger = logging.getLogger(__name__)


@shared_task
def send_course_update_notification(course_id, updated_lesson_id=None):
    """
    Отправка уведомлений об обновлении курса всем пользователям,
    которые имеют доступ к курсу
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        course = Course.objects.get(id=course_id)

        # Проверяем, обновлялся ли курс менее 4 часов назад
        time_since_update = timezone.now() - course.updated_at
        if time_since_update < timedelta(hours=4):
            logger.info(f"Курс {course.title} обновлялся менее 4 часов назад. Уведомление отложено.")
            return f"Курс обновлялся менее 4 часов назад. Уведомление не отправлено."

        # Получаем всех пользователей с доступом к курсу
        users_with_access = User.objects.filter(
            course_access__course=course,
            course_access__is_active=True
        ).distinct()

        # Получаем email'ы пользователей
        recipient_emails = [user.email for user in users_with_access if user.email]

        if not recipient_emails:
            logger.info(f"Нет получателей для курса {course.title}")
            return "Нет получателей"

        # Формируем текст письма
        if updated_lesson_id:
            try:
                lesson = Lesson.objects.get(id=updated_lesson_id, course=course)
                subject = f"Обновление курса: {course.title}"
                message = f"""
                Уважаемый пользователь!

                В курсе "{course.title}" был обновлен урок: "{lesson.title}".

                Перейдите в свой аккаунт, чтобы просмотреть обновленные материалы.

                С уважением,
                Администрация платформы
                """
            except Lesson.DoesNotExist:
                subject = f"Обновление курса: {course.title}"
                message = f"""
                Уважаемый пользователь!

                Курс "{course.title}" был обновлен.

                Перейдите в свой аккаунт, чтобы просмотреть обновленные материалы.

                С уважением,
                Администрация платформы
                """
        else:
            subject = f"Обновление курса: {course.title}"
            message = f"""
            Уважаемый пользователь!

            Курс "{course.title}" был обновлен.

            Перейдите в свой аккаунт, чтобы просмотреть обновленные материалы.

            С уважением,
            Администрация платформы
            """

        # Отправляем письма
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_emails,
            fail_silently=False,
        )

        logger.info(f"Уведомления отправлены {len(recipient_emails)} пользователям о курсе {course.title}")
        return f"Уведомления отправлены {len(recipient_emails)} пользователям"

    except Course.DoesNotExist:
        logger.error(f"Курс с id {course_id} не найден")
        return f"Курс с id {course_id} не найден"
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений: {str(e)}")
        raise e


def block_inactive_users():
    """
    Блокировка пользователей, которые не заходили более месяца
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Дата месяц назад
        one_month_ago = timezone.now() - timedelta(days=30)

        # Находим активных пользователей, которые не заходили более месяца
        # Исключаем суперпользователей (чтобы не заблокировать админа)
        inactive_users = User.objects.filter(
            is_active=True,
            last_login__lt=one_month_ago
        ).exclude(is_superuser=True)

        count = inactive_users.count()

        if count == 0:
            logger.info("Нет неактивных пользователей для блокировки")
            return "Нет пользователей для блокировки"

        # Блокируем пользователей
        for user in inactive_users:
            user.is_active = False
            user.save()
            logger.info(f"Пользователь {user.username} (ID: {user.id}) заблокирован за неактивность")

        # Отправляем уведомление администраторам (опционально)
        admin_emails = User.objects.filter(
            is_superuser=True,
            is_active=True,
            email__isnull=False
        ).values_list('email', flat=True)

        if admin_emails:
            send_mail(
                subject="Блокировка неактивных пользователей",
                message=f"Заблокировано {count} неактивных пользователей (не заходили более месяца)",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(admin_emails),
                fail_silently=True,
            )

        logger.info(f"Заблокировано {count} неактивных пользователей")
        return f"Заблокировано {count} пользователей"

    except Exception as e:
        logger.error(f"Ошибка при блокировке неактивных пользователей: {str(e)}")
        raise e