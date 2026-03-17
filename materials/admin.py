from django.contrib import admin
from .models import Course, Lesson, Payment, UserCourseAccess


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price', 'owner', 'stripe_product_id', 'stripe_price_id', 'created_at']
    list_filter = ['owner', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['stripe_product_id', 'stripe_price_id', 'created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'price', 'owner')
        }),
        ('Stripe интеграция', {
            'fields': ('stripe_product_id', 'stripe_price_id'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'course', 'order', 'owner', 'created_at']
    list_filter = ['course', 'owner']
    search_fields = ['title', 'description', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'course', 'amount', 'currency', 
        'status', 'payment_type', 'stripe_session_id', 'created_at'
    ]
    list_filter = ['status', 'payment_type', 'currency', 'created_at']
    search_fields = ['user__email', 'user__username', 'course__title', 'stripe_session_id']
    readonly_fields = [
        'stripe_session_id', 'stripe_payment_intent_id', 'stripe_customer_id',
        'stripe_invoice_id', 'stripe_subscription_id', 'created_at', 'updated_at', 'paid_at'
    ]
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'course', 'amount', 'currency', 'status', 'payment_type')
        }),
        ('Stripe данные', {
            'fields': (
                'stripe_session_id', 'stripe_payment_intent_id', 'stripe_customer_id',
                'stripe_invoice_id', 'stripe_subscription_id'
            ),
            'classes': ('collapse',)
        }),
        ('Детали платежа', {
            'fields': ('payment_method', 'last4', 'receipt_url'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserCourseAccess)
class UserCourseAccessAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'is_active', 'access_granted_at', 'access_expires_at']
    list_filter = ['is_active', 'course']
    search_fields = ['user__email', 'user__username', 'course__title']
    readonly_fields = ['access_granted_at']