"""API представления."""

import secrets

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpRequest
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import mixins, status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews.models import Category, Genre, Title, Review, Comment
from .serializers import (
    CategorySerializer, GenreSerializer, SignUpSerializer,
    TitleCreateSerializer, TitleSerializer, TokenSerializer,
    TokenResponseSerializer, UserSerializer, MeSerializer,
    ReviewSerializer, CommentSerializer
)
from .permissions import (
    AdminPermission, AdminOrReadOnlyPermission,
    ContentManagerPermission
)


User = get_user_model()


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
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
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'slug']
    lookup_field = 'slug'
    permission_classes = [AdminOrReadOnlyPermission]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = [AdminOrReadOnlyPermission]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ContentManagerPermission]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title__id=title_id)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        try:
            title = Title.objects.get(id=title_id)
        except Title.DoesNotExist:
            raise NotFound('Произведение не найдено')
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ContentManagerPermission]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review__id=review_id)

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            raise NotFound('Отзыв не найден')
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

    def get_permissions(self):
        """Переопределение прав для /users/me/."""
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request: HttpRequest) -> Response:
        """Профиль пользователя."""
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
