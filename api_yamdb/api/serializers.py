from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews.models import Category, Genre, Title

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')


class TitleCreateSerializer(serializers.ModelSerializer):
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

    def to_representation(self, instance):
        serializer = TitleSerializer(instance)
        return serializer.data


class SignUpSerializer(serializers.Serializer):
    """Регистрация пользователя."""
    
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)
    
    def validate_username(self, value):
        """Валидация username."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                "Использовать имя 'me' в качестве username запрещено."
            )
        
        import re
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                "Username может содержать только буквы, цифры и символы @, ., +, -, _"
            )
        
        return value
    
    def validate(self, data):
        """Проверка уникальности."""
        email = data.get('email')
        username = data.get('username')
        
        if User.objects.filter(email=email).exclude(username=username).exists():
            raise serializers.ValidationError({
                'email': 'Пользователь с таким email уже существует.'
            })
        
        if User.objects.filter(username=username).exclude(email=email).exists():
            raise serializers.ValidationError({
                'username': 'Пользователь с таким username уже существует.'
            })
        
        return data


class TokenSerializer(serializers.Serializer):
    """Получение JWT токена."""
    
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(write_only=True)
    
    def validate_username(self, value):
        """Проверка паттерна."""
        import re
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                "Username может содержать только буквы, цифры и символы @, ., +, -, _"
            )
        return value


class TokenResponseSerializer(serializers.Serializer):
    """Ответ с токеном."""
    
    token = serializers.CharField()
