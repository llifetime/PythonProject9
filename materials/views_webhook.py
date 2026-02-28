import json
import logging

import stripe
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .services.stripe_service import StripeService

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Эндпоинт для вебхуков от Stripe.
    Stripe отправляет сюда уведомления о событиях (успешная оплата и т.д.)
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if not sig_header:
        logger.warning("Missing Stripe signature header")
        return HttpResponseBadRequest('Missing signature')

    try:
        event = StripeService.handle_webhook_event(payload, sig_header)
        logger.info(f"Webhook processed successfully: {event['type']}")
        return HttpResponse(status=200)

    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid webhook payload: {str(e)}")
        return HttpResponseBadRequest('Invalid payload')

    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid webhook signature: {str(e)}")
        return HttpResponseBadRequest('Invalid signature')

    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return HttpResponse(status=500, content="Internal Server Error")