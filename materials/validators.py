# materials/validators.py
import re
from rest_framework import serializers


def validate_youtube_url(value):
    """
    Валидатор для проверки, что ссылка ведет только на youtube.com
    """
    if not value:
        return value

    # Проверяем, что это ссылка на YouTube
    youtube_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/'
    if not re.match(youtube_pattern, value):
        raise serializers.ValidationError(
            "Разрешены только ссылки на YouTube. Ссылки на сторонние ресурсы запрещены."
        )
    return value


class YouTubeURLValidator:
    """
    Класс-валидатор для проверки YouTube ссылок
    """

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if not value:
            return

        youtube_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/'
        if not re.match(youtube_pattern, value):
            raise serializers.ValidationError(
                {self.field: "Разрешены только ссылки на YouTube. Ссылки на сторонние ресурсы запрещены."}
            )