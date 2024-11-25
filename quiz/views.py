from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Question, UserAnswer, Answer
from .permissions import IsAllowed, HasPermission
from .serializers import QuestionSerializer, QuizGeneratorSerializer, UserAnswerSerializer, PossibleAnswersSerializer
from .using_ai import Quiz
from .tasks import delete_instances


class QuizGeneratorView(GenericAPIView):
    serializer_class = QuizGeneratorSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if 'id_of_quest' in request.session or Question.objects.filter(user=request.user).exists():
            delete_instances.delay(request.user.id) # თუ არ გაქვთ celery დაყენებული, user_answers.delete() questions.delete() ეს ჩაწერეთ ამის ნაცვლად
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_input = serializer.validated_data['text']
            ai = Quiz()
            result = ai.generate_quiz(user_input)
            if not result.message:
                if result.answers:
                    i, j = 0, result.answers_quantity
                    for question in result.questions:
                        quest = Question.objects.create(name=question, user=request.user)
                        for answer in result.answers[i:j]:
                            Answer.objects.create(name=answer, question=quest)
                        i += result.answers_quantity
                        j += result.answers_quantity
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    Question.objects.bulk_create(
                        [Question(name=question, user=request.user) for question in result.questions])
                    return Response(result, status=status.HTTP_200_OK)

            return Response({"message": "I can't generate quiz!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionView(GenericAPIView):
    queryset = Question.objects.all()
    permission_classes = [IsAuthenticated, HasPermission]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserAnswerSerializer
        return QuestionSerializer

    def get(self, request, *args, **kwargs):
        id_of_question = self.request.session.get('id_of_quest', Question.objects.filter(user=request.user).first().id)
        question = Question.objects.prefetch_related('answers').filter(id=id_of_question, user=request.user)
        if question:
            possible_answers = question.first().answers.all()
            if possible_answers:
                quest = QuestionSerializer(question.first())
                possible_answers = PossibleAnswersSerializer(possible_answers, many=True)
                return Response({"question": quest.data,
                                 'possible_answers': possible_answers.data}, status=status.HTTP_200_OK)
            else:
                serializer = QuestionSerializer(question.first())
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            self.request.session.pop('id_of_quest', None)
            return Response(
                {"message": "Quiz has ended."},
                status=status.HTTP_200_OK
            )

    def post(self, request, *args, **kwargs):
        serializer = UserAnswerSerializer(data=request.data)
        if serializer.is_valid():
            self.request.session['id_of_quest'] = self.request.session.get('id_of_quest',
                                                                           Question.objects.filter(
                                                                               user=request.user).first().id) + 1
            serializer.save(user=request.user)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FinalAnswerView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsAllowed]

    def get(self, request, *args, **kwargs):
        user_answers = UserAnswer.objects.filter(user=request.user)
        questions = Question.objects.filter(user=request.user)
        if user_answers:
            ai = Quiz()
            result = ai.evaluate_answer([answer.user_answer for answer in user_answers],
                                        [quest.name for quest in questions])
            delete_instances.delay(
                request.user.id)  # თუ არ გაქვთ celery დაყენებული, user_answers.delete() questions.delete() ეს ჩაწერეთ ამის ნაცვლად
            return Response({'result': result.point})
