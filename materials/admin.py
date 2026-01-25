from django.contrib import admin
from .models import Course, Lesson


class LessonInline(admin.TabularInline):
    """Inline для уроков в админке курса"""

    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Админ-панель для курсов"""

    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Админ-панель для уроков"""

    list_display = ('title', 'course', 'created_at', 'updated_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'description', 'video_url')