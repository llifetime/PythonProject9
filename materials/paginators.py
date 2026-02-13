from rest_framework.pagination import PageNumberPagination


class CoursePaginator(PageNumberPagination):
    """Пагинация для списка курсов"""
    page_size = 10  # Количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для изменения количества элементов
    max_page_size = 100  # Максимальное количество элементов на странице


class LessonPaginator(PageNumberPagination):
    """Пагинация для списка уроков"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 200