import stripe
import logging
from django.conf import settings
from decimal import Decimal

logger = logging.getLogger(__name__)

# Проверяем наличие ключа Stripe
if hasattr(settings, 'STRIPE_SECRET_KEY') and settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    USE_REAL_STRIPE = True
else:
    logger.warning("STRIPE_SECRET_KEY не настроен. Используется мок-режим.")
    USE_REAL_STRIPE = False


    # Создаем мок-классы для имитации Stripe
    class MockProduct:
        def __init__(self, **kwargs):
            self.id = f"prod_mock_{id(kwargs)}"


    class MockPrice:
        def __init__(self, **kwargs):
            self.id = f"price_mock_{id(kwargs)}"


    class MockSession:
        def __init__(self, **kwargs):
            self.id = f"cs_mock_{id(kwargs)}"
            self.url = "https://checkout.stripe.com/mock"
            self.payment_intent = None
            self.expires_at = None
            self.payment_status = "paid"
            self.amount_total = 9999
            self.currency = "usd"
            self.metadata = {"course_id": "1", "user_id": "1"}

        def get(self, key, default=None):
            return getattr(self, key, default)


    class MockStripe:
        class Product:
            @staticmethod
            def create(**kwargs):
                return MockProduct(**kwargs)

        class Price:
            @staticmethod
            def create(**kwargs):
                return MockPrice(**kwargs)

        class Checkout:
            class Session:
                @staticmethod
                def create(**kwargs):
                    return MockSession(**kwargs)

                @staticmethod
                def retrieve(session_id, **kwargs):
                    return MockSession(**kwargs)

        class Webhook:
            @staticmethod
            def construct_event(payload, sig_header, secret):
                return {"type": "mock.event"}


    stripe = MockStripe()


class StripeService:
    """Сервис для работы с API Stripe"""

    @staticmethod
    def create_product(course):
        """Создание продукта в Stripe"""
        try:
            product = stripe.Product.create(
                name=course.title,
                description=course.description[:500] if course.description else None,
                metadata={'course_id': course.id, 'course_title': course.title}
            )

            course.stripe_product_id = product.id
            course.save(update_fields=['stripe_product_id'])
            logger.info(f"Product created: {product.id} for course {course.id}")
            return product
        except Exception as e:
            logger.error(f"Error creating product for course {course.id}: {str(e)}")
            if not USE_REAL_STRIPE:
                # В мок-режиме возвращаем фиктивный объект
                return MockProduct()
            raise

    @staticmethod
    def create_price(course):
        """Создание цены для продукта"""
        try:
            if not course.stripe_product_id:
                StripeService.create_product(course)

            # Конвертируем в центы
            amount_in_cents = int(course.price * 100)

            price = stripe.Price.create(
                product=course.stripe_product_id,
                unit_amount=amount_in_cents,
                currency='usd',
                metadata={'course_id': course.id, 'course_price': str(course.price)}
            )

            course.stripe_price_id = price.id
            course.save(update_fields=['stripe_price_id'])
            logger.info(f"Price created: {price.id} for course {course.id}")
            return price
        except Exception as e:
            logger.error(f"Error creating price for course {course.id}: {str(e)}")
            if not USE_REAL_STRIPE:
                # В мок-режиме возвращаем фиктивный объект
                return MockPrice()
            raise

    @staticmethod
    def create_checkout_session(course, user, success_url, cancel_url):
        """Создание сессии для оплаты"""
        try:
            if not course.stripe_price_id:
                StripeService.create_price(course)

            session_params = {
                'success_url': success_url,
                'cancel_url': cancel_url,
                'payment_method_types': ['card'],
                'line_items': [{
                    'price': course.stripe_price_id,
                    'quantity': 1
                }],
                'mode': 'payment',
                'metadata': {
                    'course_id': course.id,
                    'user_id': user.id if user and user.is_authenticated else 'anonymous'
                },
                'allow_promotion_codes': True,
            }

            if user and user.is_authenticated:
                session_params['customer_email'] = user.email
                session_params['client_reference_id'] = str(user.id)

            session = stripe.checkout.Session.create(**session_params)

            return {
                'session_id': session.id,
                'url': session.url,
                'payment_intent': getattr(session, 'payment_intent', None),
                'expires_at': getattr(session, 'expires_at', None)
            }
        except Exception as e:
            logger.error(f"Error creating checkout session for course {course.id}: {str(e)}")
            if not USE_REAL_STRIPE:
                # В мок-режиме возвращаем фиктивные данные
                import uuid
                session_id = f"cs_mock_{uuid.uuid4().hex[:16]}"
                return {
                    'session_id': session_id,
                    'url': f"https://checkout.stripe.com/mock/pay/{session_id}",
                    'payment_intent': f"pi_mock_{uuid.uuid4().hex[:16]}",
                    'expires_at': None
                }
            raise

    @staticmethod
    def retrieve_session(session_id):
        """Получение информации о сессии"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {str(e)}")
            if not USE_REAL_STRIPE:
                # В мок-режиме возвращаем фиктивную сессию
                return MockSession()
            return None

    @staticmethod
    def handle_webhook_event(payload, sig_header):
        """Обработка вебхуков от Stripe"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            logger.info(f"Webhook event received: {event['type']}")
            return event
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            if not USE_REAL_STRIPE:
                # В мок-режиме возвращаем фиктивное событие
                return {"type": "checkout.session.completed", "data": {"object": {}}}
            raise