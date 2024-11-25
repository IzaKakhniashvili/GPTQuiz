from django.db import models
from user.models import CustomUser


class Question(models.Model):
    name = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class Answer(models.Model):
    name = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class UserAnswer(models.Model):
    user_answer = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
