"""Модели данных."""

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Пользователь системы."""

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
        """Роль администратора."""
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self) -> bool:
        """Роль модератора."""
        return self.role == 'moderator'


class Category(models.Model):
    """Категория произведений."""

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

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    """Жанр произведений."""

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

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    """Произведение искусства."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения',
        help_text='Укажите название произведения (например, "Тёмный рыцарь")'
    )
    year = models.IntegerField(
        verbose_name='Год выпуска',
        validators=[MinValueValidator(0),
                    MaxValueValidator(timezone.now().year)]
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        help_text='Укажите описание произведения',
        blank=True,
        default=''
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

    @property
    def rating(self) -> int | None:
        """Средний рейтинг."""
        reviews = self.reviews.all()
        if not reviews:
            return None
        return round(sum(review.score for review in reviews) / len(reviews))

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


# Промежуточная модель для связи ManyToMany между Title и Genre
class GenreTitle(models.Model):
    """Связь жанр-произведение."""

    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.title} - {self.genre}'


class Review(models.Model):
    """Отзыв пользователя."""

    title = models.ForeignKey(
        'Title',
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique_review'),
            models.CheckConstraint(
                check=models.Q(score__gte=1) & models.Q(score__lte=10),
                name='valid_score_range'
            )
        ]
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'Отзыв: {self.text[:30]}...'


class Comment(models.Model):
    """Комментарий к отзыву."""

    review = models.ForeignKey(
        Review, related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Комментарий')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.text[:30]
