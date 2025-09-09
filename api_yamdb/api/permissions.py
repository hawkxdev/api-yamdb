"""Права доступа API."""

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class AdminPermission(permissions.BasePermission):
    """Только администраторы."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Проверка прав доступа."""
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class AdminOrReadOnlyPermission(permissions.BasePermission):
    """Админ или чтение."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Проверка прав доступа."""
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class ContentManagerPermission(permissions.BasePermission):
    """Модераторы и админы."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Проверка прав доступа."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(
        self, request: Request, view: APIView, obj
    ) -> bool:
        """Проверка прав к объекту."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or obj.author == request.user
        )
