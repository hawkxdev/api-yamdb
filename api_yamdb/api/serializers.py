"""API сериализаторы."""

import re
from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()

USERNAME_PATTERN = r'^[\w.@+-]+\Z'
USERNAME_ERROR = (
    'Username может содержать только буквы, '
    'цифры и символы @, ., +, -, _'
)
FORBIDDEN_USERNAME = 'me'
FORBIDDEN_USERNAME_ERROR = (
    "Использовать имя 'me' в качестве username запрещено."
)


def validate_username_field(value: str) -> str:
    """Общая валидация username."""
    if value.lower() == FORBIDDEN_USERNAME:
        raise serializers.ValidationError(FORBIDDEN_USERNAME_ERROR)

    if not re.match(USERNAME_PATTERN, value):
        raise serializers.ValidationError(USERNAME_ERROR)

    return value


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')

    def get_rating(self, obj) -> int | None:
        """Получение среднего рейтинга."""
        if hasattr(obj, 'rating_avg'):
            return round(obj.rating_avg) if obj.rating_avg else None
        return None


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания произведений."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def to_representation(self, instance) -> dict[str, Any]:
        """Преобразует instance в словарь для сериализации.
        Args:
            instance: Объект Title для сериализации
        Returns:
            dict: Сериализованные данные
        """
        serializer = TitleSerializer(instance)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate_score(self, value: int) -> int:
        """Валидация оценки."""
        if not (1 <= value <= 10):
            raise serializers.ValidationError('Оценка должна быть от 1 до 10.')
        return value

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Валидация уникальности отзыва."""
        request = self.context.get('request')
        title_id = self.context['view'].kwargs.get('title_id')
        user = request.user
        if request.method == 'POST':
            if Review.objects.filter(title_id=title_id, author=user).exists():
                raise serializers.ValidationError(
                    'Можно оставить только один отзыв на произведение!'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class SignUpSerializer(serializers.Serializer):
    """Регистрация пользователя."""

    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    def validate_username(self, value: str) -> str:
        """Валидация username."""
        return validate_username_field(value)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Проверка уникальности."""
        email = data.get('email')
        username = data.get('username')

        if User.objects.filter(email=email).exclude(
            username=username
        ).exists():
            raise serializers.ValidationError({
                'email': 'Пользователь с таким email уже существует.'
            })

        if User.objects.filter(username=username).exclude(
            email=email
        ).exists():
            raise serializers.ValidationError({
                'username': 'Пользователь с таким username уже существует.'
            })

        return data


class TokenSerializer(serializers.Serializer):
    """Получение JWT токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(write_only=True)

    def validate_username(self, value: str) -> str:
        """Валидация username."""
        if not re.match(USERNAME_PATTERN, value):
            raise serializers.ValidationError(USERNAME_ERROR)
        return value


class TokenResponseSerializer(serializers.Serializer):
    """Ответ с токеном."""

    token = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Администрирование пользователей."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate_username(self, value: str) -> str:
        """Валидация username."""
        return validate_username_field(value)

    def validate_email(self, value: str) -> str:
        """Валидация email."""
        if self.instance is None:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким email уже существует.'
                )
        else:
            if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким email уже существует.'
                )
        return value


class MeSerializer(serializers.ModelSerializer):
    """Профиль пользователя."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)

    def validate_username(self, value: str) -> str:
        """Валидация username."""
        return validate_username_field(value)
