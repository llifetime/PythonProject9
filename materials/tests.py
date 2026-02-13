# materials/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Course, Lesson
from users.models import Subscription

User = get_user_model()


class LessonTestCase(APITestCase):
    """Тестирование CRUD операций для уроков"""

    def setUp(self):
        """Подготовка тестовых данных"""
        # Создаем пользователей
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            username='testuser'
        )

        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123',
            username='otheruser'
        )

        # Создаем группу модераторов
        self.moderator_group, _ = Group.objects.get_or_create(name='Модераторы')

        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='testpass123',
            username='moderator'
        )
        self.moderator.groups.add(self.moderator_group)

        # Создаем курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user,
            price=1000
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Lesson Description',
            course=self.course,
            owner=self.user,
            video_url='https://www.youtube.com/watch?v=test123'
        )

        self.client = APIClient()

    def test_create_lesson_authenticated(self):
        """Тест создания урока авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)

        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'course': self.course.id,
            'video_url': 'https://www.youtube.com/watch?v=new123'
        }

        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_unauthenticated(self):
        """Тест создания урока неавторизованным пользователем"""
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'course': self.course.id,
        }

        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_lesson_with_invalid_youtube_url(self):
        """Тест создания урока с недопустимой ссылкой"""
        self.client.force_authenticate(user=self.user)

        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'course': self.course.id,
            'video_url': 'https://vimeo.com/123456'
        }

        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_url', response.data)

    def test_update_lesson_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.user)

        data = {
            'title': 'Updated Lesson Title'
        }

        response = self.client.patch(f'/api/lessons/{self.lesson.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson Title')

    def test_update_lesson_other_user(self):
        """Тест обновления урока другим пользователем"""
        self.client.force_authenticate(user=self.other_user)

        data = {
            'title': 'Updated Lesson Title'
        }

        response = self.client.patch(f'/api/lessons/{self.lesson.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lesson_moderator(self):
        """Тест обновления урока модератором"""
        self.client.force_authenticate(user=self.moderator)

        data = {
            'title': 'Updated by Moderator'
        }

        response = self.client.patch(f'/api/lessons/{self.lesson.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated by Moderator')

    def test_delete_lesson_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_moderator(self):
        """Тест удаления урока модератором (должен быть запрещен)"""
        self.client.force_authenticate(user=self.moderator)

        response = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_lessons_authenticated(self):
        """Тест получения списка уроков авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)  # Пагинация


class SubscriptionTestCase(APITestCase):
    """Тестирование функционала подписки"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            username='testuser'
        )

        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123',
            username='otheruser'
        )

        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user,
            price=1000
        )

        self.client = APIClient()

    def test_subscribe_to_course(self):
        """Тест подписки на курс"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(f'/api/courses/{self.course.id}/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(
            user=self.user, course=self.course
        ).exists())

    def test_unsubscribe_from_course(self):
        """Тест отписки от курса"""
        self.client.force_authenticate(user=self.user)

        # Сначала подписываемся
        Subscription.objects.create(user=self.user, course=self.course)

        # Затем отписываемся
        response = self.client.post(f'/api/courses/{self.course.id}/unsubscribe/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Subscription.objects.filter(
            user=self.user, course=self.course
        ).exists())

    def test_course_serializer_shows_subscription_status(self):
        """Тест отображения статуса подписки в сериализаторе курса"""
        self.client.force_authenticate(user=self.user)

        # Подписываемся на курс
        Subscription.objects.create(user=self.user, course=self.course)

        response = self.client.get(f'/api/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

        # Проверяем для другого пользователя
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'/api/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_subscribed'])

    def test_subscribe_twice_prevented(self):
        """Тест предотвращения повторной подписки"""
        self.client.force_authenticate(user=self.user)

        # Подписываемся первый раз
        response1 = self.client.post(f'/api/courses/{self.course.id}/subscribe/')

        # Подписываемся второй раз
        response2 = self.client.post(f'/api/courses/{self.course.id}/subscribe/')

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['status'], 'already_subscribed')
        self.assertEqual(Subscription.objects.filter(
            user=self.user, course=self.course
        ).count(), 1)


class PaginationTestCase(APITestCase):
    """Тестирование пагинации"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            username='testuser'
        )

        # Создаем 15 курсов
        for i in range(15):
            Course.objects.create(
                title=f'Course {i}',
                description=f'Description {i}',
                owner=self.user,
                price=1000 * i
            )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_course_pagination(self):
        """Тест пагинации курсов"""
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем структуру ответа с пагинацией
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        # Проверяем количество на странице (по умолчанию 10)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], 15)
        self.assertIsNotNone(response.data['next'])

    def test_pagination_with_custom_page_size(self):
        """Тест пагинации с кастомным размером страницы"""
        response = self.client.get('/api/courses/?page_size=5')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

        response = self.client.get('/api/courses/?page_size=20')
        self.assertEqual(len(response.data['results']), 15)  # Все курсы

    def test_second_page(self):
        """Тест второй страницы пагинации"""
        response = self.client.get('/api/courses/?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # Оставшиеся 5