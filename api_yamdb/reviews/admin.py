"""Админ панель Django."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import QuerySet
from .models import Category, Genre, Title, GenreTitle, User, Review, Comment


class GenreTitleInline(admin.TabularInline):
    """Inline жанров произведения."""

    model = GenreTitle
    extra = 1


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Админ произведений."""

    list_display = ('name', 'year', 'category', 'display_genre')
    list_filter = ('category', 'year', 'genre')
    search_fields = ('name', 'category__name', 'genre__name')
    inlines = [GenreTitleInline]
    list_editable = ('year', 'category')

    def display_genre(self, obj: Title) -> str:
        """Отображает список жанров произведения в админке.
        Args:
            obj: Объект Title
        Returns:
            str: Строка с перечислением жанров
        """
        return ', '.join([genre.name for genre in obj.genre.all()])
    display_genre.short_description = 'Жанры'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ категорий."""

    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('slug',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Админ жанров."""

    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('slug',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админ отзывов."""

    list_display = ('title', 'author', 'score', 'pub_date')
    list_filter = ('score', 'pub_date', 'title__category')
    search_fields = ('text', 'author__username', 'title__name')
    list_editable = ('score',)
    date_hierarchy = 'pub_date'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админ комментариев."""

    list_display = ('review', 'author', 'pub_date')
    list_filter = ('pub_date', 'review__title')
    search_fields = ('text', 'author__username')
    date_hierarchy = 'pub_date'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ для кастомной модели пользователя."""

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительные поля', {
            'fields': ('bio', 'role', 'confirmation_code')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительные поля', {
            'fields': ('bio', 'role')
        }),
    )
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_editable = ('role',)
