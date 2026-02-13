# users/management/commands/create_payments.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Payment
from decimal import Decimal
from django.utils import timezone


class Command(BaseCommand):
    help = 'Создание тестовых платежей'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Проверяем какие поля есть у модели User
        user_fields = [f.name for f in User._meta.fields]
        self.stdout.write(f'Поля модели User: {user_fields}')

        # Создаем тестовых пользователей
        users_data = [
            {
                'email': 'admin@example.com',
                'password': 'admin123',
                'first_name': 'Администратор',
                'last_name': 'Системы',
                'is_staff': True,
                'is_superuser': True
            },
            {
                'email': 'student1@example.com',
                'password': 'student123',
                'first_name': 'Иван',
                'last_name': 'Петров'
            },
            {
                'email': 'student2@example.com',
                'password': 'student123',
                'first_name': 'Мария',
                'last_name': 'Иванова'
            }
        ]

        created_users = []
        for user_data in users_data:
            email = user_data['email']

            # Проверяем, существует ли пользователь
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                self.stdout.write(f'Пользователь уже существует: {user.email}')
            else:
                # Создаем пользователя
                try:
                    # Пробуем создать суперпользователя если указаны флаги
                    if user_data.get('is_superuser', False):
                        user = User.objects.create_superuser(
                            email=email,
                            password=user_data['password'],
                            first_name=user_data.get('first_name', ''),
                            last_name=user_data.get('last_name', '')
                        )
                    else:
                        user = User.objects.create_user(
                            email=email,
                            password=user_data['password'],
                            first_name=user_data.get('first_name', ''),
                            last_name=user_data.get('last_name', '')
                        )

                    self.stdout.write(f'Создан пользователь: {user.email}')
                except Exception as e:
                    # Если не работает create_user, создаем вручную
                    self.stdout.write(f'Ошибка при создании пользователя: {e}')
                    self.stdout.write('Пробуем создать вручную...')

                    user_data_copy = user_data.copy()
                    password = user_data_copy.pop('password')
                    user = User(**user_data_copy)
                    user.set_password(password)
                    user.save()
                    self.stdout.write(f'Пользователь создан вручную: {user.email}')

            created_users.append(user)

        # Создаем тестовые платежи
        payments_data = [
            {
                'user': created_users[0],  # admin
                'amount': '25000.00',
                'payment_method': 'transfer',
                'description': 'Оплата годовой подписки'
            },
            {
                'user': created_users[1],  # student1
                'amount': '15000.00',
                'payment_method': 'transfer',
                'description': 'Оплата курса Python'
            },
            {
                'user': created_users[1],  # student1
                'amount': '5000.00',
                'payment_method': 'cash',
                'description': 'Оплата индивидуального урока'
            },
            {
                'user': created_users[2],  # student2
                'amount': '18000.00',
                'payment_method': 'transfer',
                'description': 'Оплата курса Django'
            },
            {
                'user': created_users[2],  # student2
                'amount': '3000.00',
                'payment_method': 'cash',
                'description': 'Оплата консультации'
            }
        ]

        # Удаляем старые тестовые платежи (опционально)
        Payment.objects.all().delete()
        self.stdout.write('Старые платежи удалены')

        payments = []
        for i, data in enumerate(payments_data, 1):
            payment = Payment(
                user=data['user'],
                payment_date=timezone.now(),
                amount=Decimal(data['amount']),
                payment_method=data['payment_method']
            )
            payments.append(payment)

        Payment.objects.bulk_create(payments)

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Успешно создано:\n'
                f'• Пользователей: {len(created_users)}\n'
                f'• Платежей: {len(payments)}\n'
                f'\n📋 Данные для входа:\n'
                f'• {created_users[0].email} / admin123 (администратор)\n'
                f'• {created_users[1].email} / student123\n'
                f'• {created_users[2].email} / student123\n'
                f'\n💳 Пример платежей:\n'
            )
        )

        # Показываем примеры созданных платежей
        for payment in Payment.objects.all()[:3]:
            self.stdout.write(f'  - {payment.user.email}: {payment.amount} руб. ({payment.payment_method})')