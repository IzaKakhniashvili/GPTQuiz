from celery import shared_task
from .models import UserAnswer, Question

@shared_task
def delete_instances(current_user_id):
    UserAnswer.objects.filter(user_id=current_user_id).delete()
    Question.objects.filter(user_id=current_user_id).delete()

    print("Deleted Successfully")
