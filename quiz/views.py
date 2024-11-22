from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Topic, Question
from .serializers import TopicSerializer, QuestionSerializer
from openai import OpenAI

client = OpenAI()

class GenerateQuestionsAPIView(APIView):
    def post(self, request):
        topic_name = request.data.get('topic', '').strip()
        if not topic_name:
            return Response({"error": "Topic is required"}, status=status.HTTP_400_BAD_REQUEST)
    
        
        # Save topic to DB
        subject = Topic.objects.create(name=topic_name)
        
        try:
            # Generate questions via ChatGPT using client.chat.completions.create
            response = client.chat.completions.create(
                model="gpt-4",  # Correct model name
                messages=[
                    {"role": "user", "content": f"Generate 10 questions about {topic_name}"}
                ]
            )
            
            # Extract questions from the response
            response = response.choices[0].message.content
            questions = response.split('\n') 
        except Exception as e:
            return Response({"error": f"OpenAI API call failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save questions to DB
        question_objects = [Question(topic=subject, text=q) for q in questions]
        Question.objects.bulk_create(question_objects)

        serializer = QuestionSerializer(question_objects, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class ValidateAnswersAPIView(APIView):
    def post(self, request):
        answers = request.data.get('answers', [])
        if not answers:
            return Response({"error": "Answers are required"}, status=status.HTTP_400_BAD_REQUEST)

        validated_answers = []
        for answer in answers:
            question = answer.get('question')
            user_answer = answer.get('answer')

            if not question or not user_answer:
                return Response({"error": "Both question and answer are required in each answer pair."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Validate via OpenAI using client.chat.completions.create
                chat_response = client.chat.completions.create(
                    model="gpt-4",  # Correct model name
                    messages=[
                        {"role": "user", "content": f"Question: {question}\nAnswer: {user_answer}\nIs this correct?"}
                    ]
                )

                # Extract feedback from the response
                feedback = chat_response.choices[0].message.content

                # Check if the answer is correct based on feedback
                is_correct = "correct" in feedback.lower()

            except Exception as e:
                return Response({"error": f"OpenAI API call failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            validated_answers.append({
                "question": question,
                "user_answer": user_answer,
                "is_correct": is_correct,
                "feedback": feedback,
            })

        return Response(validated_answers, status=status.HTTP_200_OK)
    


# Create your views here.
