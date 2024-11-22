from django.db import models

class Topic(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name()
    
    
class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    user_answer = models.TextField()
    is_correct = models.BooleanField(default = False)
    feedback = models.TextField(null = True, blank=True)
