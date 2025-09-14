"""API представления."""

import secrets

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title

from .filters import TitleFilter
from .permissions import (AdminOrReadOnlyPermission, AdminPermission,
                          ContentManagerPermission)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, MeSerializer, ReviewSerializer,
                          SignUpSerializer, TitleCreateSerializer,
                          TitleSerializer, TokenResponseSerializer,
                          TokenSerializer, UserSerializer)

User = get_user_model()


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Управление категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'slug']
    lookup_field = 'slug'
    permission_classes = [AdminOrReadOnlyPermission]


class GenreViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """Управление жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'slug']
    lookup_field = 'slug'
    permission_classes = [AdminOrReadOnlyPermission]


class TitleViewSet(viewsets.ModelViewSet):
    """Управление произведениями."""

    queryset = Title.objects.with_rating()

    permission_classes = [AdminOrReadOnlyPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Выбор сериализатора."""
        if self.action in ['create', 'update', 'partial_update']:
            return TitleCreateSerializer
        return TitleSerializer

    def get_queryset(self) -> QuerySet:
        """Фильтрация произведений с аннотацией рейтинга."""
        queryset = Title.objects.with_rating()

        queryset = self.filter_queryset(queryset)

        return queryset


class ReviewViewSet(viewsets.ModelViewSet):
    """Управление отзывами."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ContentManagerPermission]

    def get_queryset(self) -> QuerySet:
        """Получение отзывов."""
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(
            title__id=title_id
        ).select_related('author', 'title')

    def perform_create(self, serializer: BaseSerializer) -> None:
        """Создание отзыва."""
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Управление комментариями."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ContentManagerPermission]

    def get_queryset(self) -> QuerySet:
        """Получение комментариев."""
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(
            review__id=review_id
        ).select_related('author', 'review__title')

    def perform_create(self, serializer: BaseSerializer) -> None:
        """Создание комментария."""
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)


class SignUpView(APIView):
    """Регистрация пользователя."""

    permission_classes = [AllowAny]

    def post(self, request: HttpRequest) -> Response:
        """POST метод регистрации."""
        serializer = SignUpSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']

            confirmation_code = secrets.token_hex(16)  # 32 символа

            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )

            if not created and user.email != email:
                return Response(
                    {
                        'detail': (
                            'Пользователь с таким username уже существует.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.confirmation_code = confirmation_code
            user.save()

            send_mail(
                subject='Код подтверждения YaMDb',
                message=f'Ваш код подтверждения: {confirmation_code}',
                from_email='noreply@yamdb.com',
                recipient_list=[email],
                fail_silently=False,
            )

            return Response(
                {'email': email, 'username': username},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(APIView):
    """Получение JWT токена."""

    permission_classes = [AllowAny]

    def post(self, request: HttpRequest) -> Response:
        """POST метод получения токена."""
        serializer = TokenSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            confirmation_code = serializer.validated_data['confirmation_code']

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response(
                    {'detail': 'Пользователь не найден.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if user.confirmation_code != confirmation_code:
                return Response(
                    {'detail': 'Неверный код подтверждения.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response_data = {'token': access_token}
            response_serializer = TokenResponseSerializer(data=response_data)
            response_serializer.is_valid()

            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Управление пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'
    permission_classes = [AdminPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self) -> list[permissions.BasePermission]:
        """Переопределение прав."""
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['get', 'patch', 'delete'])
    def me(self, request: HttpRequest) -> Response:
        """Профиль пользователя."""
        if request.method == 'DELETE':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if request.method == 'GET':
            serializer = MeSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = MeSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
