from django.urls import path
from .views import GenerateQuestionsAPIView, ValidateAnswersAPIView

app_name = 'quiz'


urlpatterns = [
    path('generate-questions/', GenerateQuestionsAPIView.as_view(), name='generate-questions'),
    path('validate-answers/', ValidateAnswersAPIView.as_view(), name='validate-answers'),
]