import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

from reviews.models import current_year_max_validator


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Укажите название категории (например, "Фильмы")',
                 max_length=256, verbose_name='Название категории')),
                ('slug', models.SlugField(help_text='Укажите уникальный slug для категории. Используйте только латиницу, цифры,дефисы и знаки подчёркивания. Например: "movies" для раздела фильмов.',
                 unique=True, verbose_name='Slug категории')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Укажите название жанра (например, "Комедия")',
                 max_length=256, verbose_name='Название жанра')),
                ('slug', models.SlugField(help_text='Укажите уникальный slug для жанра. Используйте только латиницу, цифры,дефисы и знаки подчёркивания. Например: "comedy" для жанра комедий.', unique=True, verbose_name='Slug жанра')),
            ],
            options={
                'verbose_name': 'Жанр',
                'verbose_name_plural': 'Жанры',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False,
                 help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                 max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False,
                 help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(
                    default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('bio', models.TextField(blank=True, help_text='Расскажите о себе', max_length=1000, verbose_name='Биография')),
                ('role', models.CharField(choices=[('user', 'Пользователь'), ('moderator', 'Модератор'), (
                    'admin', 'Администратор')], default='user', help_text='Роль пользователя', max_length=20, verbose_name='Роль')),
                ('confirmation_code', models.CharField(blank=True, help_text='Код для подтверждения email',
                 max_length=255, verbose_name='Код подтверждения')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                 related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.',
                 related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ('username',),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст отзыва')),
                ('score', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(
                    1), django.core.validators.MaxValueValidator(10)], verbose_name='Оценка')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='reviews', to=settings.AUTH_USER_MODEL, verbose_name='Автор отзыва')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Комментарий')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор комментария')),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='comments', to='reviews.review', verbose_name='Отзыв')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название произведения')),
                ('year', models.IntegerField(validators=[django.core.validators.MinValueValidator(
                    0), current_year_max_validator], verbose_name='Год выпуска')),
                ('description', models.TextField(blank=True, default='', verbose_name='Описание произведения')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                 related_name='titles', to='reviews.category', verbose_name='Категория')),
                ('genre', models.ManyToManyField(blank=True, related_name='titles', to='reviews.genre', verbose_name='Жанр')),
            ],
            options={
                'verbose_name': 'Произведение',
                'verbose_name_plural': 'Произведения',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='review',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='reviews', to='reviews.title', verbose_name='Произведение'),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('title', 'author'), name='unique_review'),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.CheckConstraint(condition=models.Q(
                ('score__gte', 1), ('score__lte', 10)), name='valid_score_range'),
        ),
    ]
