from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, GenreViewSet,
                    TitleViewSet, ReviewViewSet, CommentViewSet)

app_name = 'api'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'titles', TitleViewSet, basename='titles')
reviews_router.register(r'reviews', ReviewViewSet, basename='reviews')

comments_router = DefaultRouter()
comments_router.register(r'comments', CommentViewSet, basename='comments')
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/titles/<int:title_id>/', include(reviews_router.urls)),
    path(
        'v1/titles/<int:title_id>/reviews/<int:review_id>/',
        include(comments_router.urls)),
]
