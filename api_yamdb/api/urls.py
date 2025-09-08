from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet,
)

app_name = 'api'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/', include(router.urls)),
    path(
        'v1/titles/<int:title_id>/reviews/',
        ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='review-list',
    ),
    path(
        'v1/titles/<int:title_id>/reviews/<int:pk>/',
        ReviewViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='review-detail',
    ),
    path(
        'v1/titles/<int:title_id>/reviews/<int:review_id>/comments/',
        CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='comment-list',
    ),
    path(
        'v1/titles/<int:title_id>/reviews/<int:review_id>/comments/<int:pk>/',
        CommentViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='comment-detail',
    ),
]
