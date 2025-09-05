"""Модели приложения reviews."""

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Кастомная модель пользователя."""

    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]

    bio = models.TextField(
        'Биография',
        blank=True,
        help_text='Расскажите о себе'
    )
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        help_text='Роль пользователя'
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=255,
        blank=True,
        help_text='Код для подтверждения email'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self) -> str:
        return self.username

    @property
    def is_admin(self) -> bool:
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self) -> bool:
        return self.role == 'moderator'


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название категории',
        help_text='Укажите название категории (например, "Фильмы")'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug категории',
        help_text=('Укажите уникальный slug для категории. '
                   'Используйте только латиницу, цифры,'
                   'дефисы и знаки подчёркивания. '
                   'Например: "movies" для раздела фильмов.')
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название жанра',
        help_text='Укажите название жанра (например, "Комедия")'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug жанра',
        help_text=('Укажите уникальный slug для жанра. '
                   'Используйте только латиницу, цифры,'
                   'дефисы и знаки подчёркивания. '
                   'Например: "comedy" для жанра комедий.')
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения',
        help_text='Укажите название произведения (например, "Тёмный рыцарь")'
    )
    year = models.IntegerField(
        verbose_name='Год выпуска',
        help_text='Укажите год выпуска произведения',
        validators=[MinValueValidator(0), MaxValueValidator(2025)]
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        help_text='Укажите описание произведения',
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        blank=True,
        verbose_name='Жанр',
        help_text='Выберите жанр(ы) для произведения',
        related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Категория',
        help_text='Выберите категорию для произведения',
        related_name='titles'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


# Промежуточная модель для связи ManyToMany между Title и Genre
class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} - {self.genre}'
