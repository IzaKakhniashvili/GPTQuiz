from rest_framework.permissions import BasePermission
from .models import UserAnswer, Question


class IsAllowed(BasePermission):
    def has_permission(self, request, view):
        return UserAnswer.objects.filter(user=request.user).count() == Question.objects.filter(
            user=request.user).count()


class HasPermission(BasePermission):
    message = "You should generate quiz first!"

    def has_permission(self, request, view):
        return Question.objects.filter(user=request.user).exists()
