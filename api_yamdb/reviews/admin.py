from django.contrib import admin
from .models import Category, Genre, Title, GenreTitle


class GenreTitleInline(admin.TabularInline):
    model = GenreTitle
    extra = 1


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category', 'display_genre')
    list_filter = ('category', 'year', 'genre')
    search_fields = ('name', 'category__name', 'genre__name')
    inlines = [GenreTitleInline]

    def display_genre(self, obj):
        return ', '.join([genre.name for genre in obj.genre.all()])
    display_genre.short_description = 'Жанры'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
