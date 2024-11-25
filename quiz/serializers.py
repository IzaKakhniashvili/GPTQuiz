from rest_framework import serializers
from .models import Question, UserAnswer, Answer


class QuizGeneratorSerializer(serializers.Serializer):
    text = serializers.CharField()


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'name')


class PossibleAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('name',)


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ('user_answer',)
