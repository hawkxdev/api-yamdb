"""Импорт CSV данных"""

import csv

from django.core.management.base import BaseCommand
from reviews.models import Category, Genre, GenreTitle, Title


class Command(BaseCommand):
    """Команда импорт данных"""
    help = (
        'Импорт данных из CSV файлов для '
        'категорий, жанров, произведений и их связей'
    )

    def import_categories(self) -> None:
        """Импорт категорий из CSV файла."""
        try:
            with open('static/data/category.csv', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    Category.objects.get_or_create(
                        id=row['id'],
                        name=row['name'],
                        slug=row['slug']
                    )
                self.stdout.write(
                    self.style.SUCCESS('Категории успешно импортированы')
                )
        except FileNotFoundError:
            self.stdout.write(
                self.style.WARNING('Файл category.csv не найден')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при импорте категорий: {e}')
            )

    def import_genres(self):
        """Импорт жанров из CSV файла."""
        try:
            with open('static/data/genre.csv', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    Genre.objects.get_or_create(
                        id=row['id'],
                        name=row['name'],
                        slug=row['slug']
                    )
                self.stdout.write(
                    self.style.SUCCESS('Жанры успешно импортированы')
                )
        except FileNotFoundError:
            self.stdout.write(
                self.style.WARNING('Файл genre.csv не найден')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при импорте жанров: {e}')
            )

    def import_titles(self):
        """Импорт произведений из CSV файла."""
        try:
            with open('static/data/titles.csv', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    category = Category.objects.get(id=row['category'])
                    Title.objects.get_or_create(
                        id=row['id'],
                        name=row['name'],
                        year=row['year'],
                        category=category
                    )
                self.stdout.write(
                    self.style.SUCCESS('Произведения успешно импортированы')
                )
        except FileNotFoundError:
            self.stdout.write(
                self.style.WARNING('Файл titles.csv не найден')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при импорте произведений: {e}')
            )

    def import_genre_relations(self):
        """Импорт связей между жанрами и произведениями из CSV файла."""
        try:
            with open('static/data/genre_title.csv', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])
                    GenreTitle.objects.get_or_create(title=title, genre=genre)
                self.stdout.write(
                    self.style.SUCCESS('Связи жанров успешно импортированы')
                )
        except FileNotFoundError:
            self.stdout.write(
                self.style.WARNING('Файл genre_title.csv не найден')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при импорте связей жанров: {e}')
            )

    def handle(self, *args, **options) -> None:
        """Основной метод выполнения команды."""
        self.stdout.write('Начинаем импорт данных...')

        self.import_categories()
        self.import_genres()
        self.import_titles()
        self.import_genre_relations()

        self.stdout.write(self.style.SUCCESS('\nИмпорт завершен!'))
        self.stdout.write(f'Категорий: {Category.objects.count()}')
        self.stdout.write(f'Жанров: {Genre.objects.count()}')
        self.stdout.write(f'Произведений: {Title.objects.count()}')
        self.stdout.write(
            f'Связей жанров и произведений: {GenreTitle.objects.count()}'
        )
