# materials/tests_all_endpoints.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from materials.models import Course, Lesson
from users.models import Payment, Subscription
from decimal import Decimal
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class CompleteAPITestCase(APITestCase):
    """Полное тестирование всех эндпоинтов API"""

    def setUp(self):
        # Создаем пользователей
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            username='testuser',
            first_name='Test',
            last_name='User',
            city='Moscow'
        )

        self.admin = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass123',
            username='admin'
        )

        # Создаем группу модераторов
        self.moderator_group, _ = Group.objects.get_or_create(name='Модераторы')
        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='modpass123',
            username='moderator'
        )
        self.moderator.groups.add(self.moderator_group)

        # Создаем тестовые данные
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user,
            price=Decimal('1500.00')
        )

        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Lesson Description',
            course=self.course,
            owner=self.user,
            video_url='https://www.youtube.com/watch?v=test123'
        )

        self.payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('1500.00'),
            payment_method='transfer',
            course=self.course
        )

        self.client = APIClient()

    # Тесты аутентификации
    def test_jwt_token_obtain(self):
        """Тест получения JWT токена"""
        response = self.client.post('/api/token/', {
            'email': 'user@test.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_jwt_token_refresh(self):
        """Тест обновления JWT токена"""
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post('/api/token/refresh/', {
            'refresh': str(refresh)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_registration(self):
        """Тест регистрации нового пользователя"""
        data = {
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4)  # user, admin, moderator, new

    # Тесты курсов
    def test_courses_list_pagination(self):
        """Тест списка курсов с пагинацией"""
        # Создаем дополнительные курсы
        for i in range(15):
            Course.objects.create(
                title=f'Course {i}',
                owner=self.user
            )

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 10)

    def test_course_detail_with_subscription_status(self):
        """Тест деталей курса со статусом подписки"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_subscribed', response.data)
        self.assertFalse(response.data['is_subscribed'])

        # Подписываемся
        Subscription.objects.create(user=self.user, course=self.course)
        response = self.client.get(f'/api/courses/{self.course.id}/')
        self.assertTrue(response.data['is_subscribed'])

    def test_course_create_by_moderator_forbidden(self):
        """Тест запрета создания курса модератором"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            'title': 'New Course',
            'description': 'Description'
        }
        response = self.client.post('/api/courses/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_update_by_moderator_allowed(self):
        """Тест разрешения обновления курса модератором"""
        self.client.force_authenticate(user=self.moderator)
        data = {'title': 'Updated by Moderator'}
        response = self.client.patch(f'/api/courses/{self.course.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated by Moderator')

    # Тесты уроков
    def test_lesson_create_with_valid_youtube_url(self):
        """Тест создания урока с валидной YouTube ссылкой"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Lesson',
            'course': self.course.id,
            'video_url': 'https://www.youtube.com/watch?v=new123'
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_create_with_invalid_youtube_url(self):
        """Тест создания урока с невалидной ссылкой"""
        self.client.force_authenticate(user=self.user)
        invalid_urls = [
            'https://vimeo.com/123456',
            'https://rutube.ru/video/123/',
            'https://example.com/video.mp4'
        ]
        for url in invalid_urls:
            data = {
                'title': 'New Lesson',
                'course': self.course.id,
                'video_url': url
            }
            response = self.client.post('/api/lessons/', data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_create_by_moderator_forbidden(self):
        """Тест запрета создания урока модератором"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            'title': 'New Lesson',
            'course': self.course.id,
            'video_url': 'https://www.youtube.com/watch?v=new123'
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Тесты платежей
    def test_payments_list_filtering(self):
        """Тест фильтрации платежей"""
        self.client.force_authenticate(user=self.user)

        # Фильтр по методу оплаты
        response = self.client.get('/api/payments/?payment_method=transfer')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Фильтр по курсу
        response = self.client.get(f'/api/payments/?course={self.course.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payments_ordering(self):
        """Тест сортировки платежей"""
        # Создаем дополнительный платеж
        Payment.objects.create(
            user=self.user,
            amount=500.00,
            payment_method='cash'
        )

        self.client.force_authenticate(user=self.user)

        # По умолчанию сортировка по убыванию даты
        response = self.client.get('/api/payments/')
        dates = [item['payment_date'] for item in response.data]
        self.assertEqual(dates, sorted(dates, reverse=True))

        # Сортировка по возрастанию
        response = self.client.get('/api/payments/?ordering=payment_date')
        dates = [item['payment_date'] for item in response.data]
        self.assertEqual(dates, sorted(dates))

    # Тесты профиля пользователя
    def test_user_profile_with_payment_history(self):
        """Тест профиля пользователя с историей платежей"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что в ответе есть данные пользователя
        self.assertEqual(response.data['email'], 'user@test.com')

    def test_own_profile_only(self):
        """Тест доступа только к своему профилю"""
        self.client.force_authenticate(user=self.user)

        # Свой профиль - доступен
        response = self.client.get(f'/api/profile/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Чужой профиль - 404 (фильтр по id)
        response = self.client.get(f'/api/profile/{self.admin.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Тесты подписок
    def test_subscription_lifecycle(self):
        """Тест полного цикла подписки"""
        self.client.force_authenticate(user=self.user)

        # Проверяем, что подписки нет
        self.assertFalse(Subscription.objects.filter(
            user=self.user, course=self.course
        ).exists())

        # Подписываемся
        response = self.client.post(f'/api/courses/{self.course.id}/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что подписка создана
        self.assertTrue(Subscription.objects.filter(
            user=self.user, course=self.course
        ).exists())

        # Пытаемся подписаться повторно
        response = self.client.post(f'/api/courses/{self.course.id}/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'already_subscribed')

        # Отписываемся
        response = self.client.post(f'/api/courses/{self.course.id}/unsubscribe/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что подписка удалена
        self.assertFalse(Subscription.objects.filter(
            user=self.user, course=self.course
        ).exists())

        # Отписываемся повторно
        response = self.client.post(f'/api/courses/{self.course.id}/unsubscribe/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'not_subscribed')

    def test_subscription_requires_authentication(self):
        """Тест требования аутентификации для подписки"""
        # Без аутентификации
        response = self.client.post(f'/api/courses/{self.course.id}/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscription_to_nonexistent_course(self):
        """Тест подписки на несуществующий курс"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/courses/999/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# Запуск тестов с покрытием:
# coverage run --source='.' manage.py test
# coverage report