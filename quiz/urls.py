from django.urls import path
from .views import QuizGeneratorView, QuestionView, FinalAnswerView

app_name = 'quiz'

urlpatterns = [
    path('', QuizGeneratorView.as_view(), name='quiz-generator'),
    path('questions/', QuestionView.as_view(), name='questions'),
    path('answer/', FinalAnswerView.as_view(), name='answer'),
]
