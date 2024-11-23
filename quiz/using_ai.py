import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from typing import List

load_dotenv()


class AboutQuiz(BaseModel):
    message: str
    questions: List[str]
    answers: List[str]


class QuizPoint(BaseModel):
    point: str


class Quiz:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'))

    def generate_quiz(self, user_input):
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system",
                 "content": "If the user prompt gibberish text or wants to generate more than 15 questions, fill 'message' attribute else ignore 'message' attribute. By default, return questions only without possible answers, but include the correct answers in the 'answers' attribute of each question."},
                {"role": "user", "content": user_input},
            ],
            response_format=AboutQuiz,
        )
        return response.choices[0].message.parsed

    def evaluate_answer(self, user_answers, questions):
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system",
                 "content": f"You should evaluate user total point based on the user answers {user_answers} and that's questions {questions}.You should evaluate the point in that format: Total_User_Point/Question_Quantity."},
            ],
            response_format=QuizPoint,
        )
        return response.choices[0].message.parsed
