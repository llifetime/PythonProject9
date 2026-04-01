# users/filters.py
import django_filters
from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    ordering = django_filters.OrderingFilter(
        fields=(
            ('payment_date', 'payment_date'),
            ('-payment_date', '-payment_date'),
            ('amount', 'amount'),
        ),
        field_labels={
            'payment_date': 'По дате (возрастание)',
            '-payment_date': 'По дате (убывание)',
            'amount': 'По сумме',
        }
    )

    payment_method = django_filters.ChoiceFilter(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        label='Способ оплаты'
    )

    class Meta:
        model = Payment
        fields = {
            'paid_course': ['exact'],
            'paid_lesson': ['exact'],
            'payment_method': ['exact'],
            'amount': ['gte', 'lte'],
        }