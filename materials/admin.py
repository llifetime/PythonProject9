# materials/admin.py
from django.contrib import admin
from .models import Course, Lesson

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price')  # Убрали created_at, updated_at
    list_filter = ('price',)  # Убрали created_at
    search_fields = ('title', 'description')
    ordering = ('-id',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'order')  # Убрали created_at, updated_at
    list_filter = ('course', 'order')  # Убрали created_at
    search_fields = ('title', 'description')
    ordering = ('course', 'order')