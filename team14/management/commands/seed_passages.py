import random
from django.core.management.base import BaseCommand
from team14.models import Passage, Question, Option


class Command(BaseCommand):
    help = "Seed database with passages, questions, and options"

    def handle(self, *args, **kwargs):
        topics = ['biology', 'history', 'astronomy', 'geology', 'anthropology']
        difficulties = ['easy', 'medium', 'hard']
        question_types = [
            'factual',
            'negative_factual',
            'inference',
            'vocabulary',
        ]

        Passage.objects.all().delete()  # ⚠️ اگر نمی‌خوای پاک بشه، این خط رو حذف کن

        for i in range(1, 101):
            passage_text = (
                f"This is the text of passage number {i}. "
                "It is generated for testing and development purposes. "
                "The content simulates an academic reading passage."
            )

            passage = Passage.objects.create(
                title=f"Passage {i}",
                text=passage_text,
                topic=random.choice(topics),
                difficulty_level=random.choice(difficulties),
                text_length=len(passage_text.split()),
                rubric_version="v1.0",
                version=1,
            )

            # هر Passage = 3 سؤال
            for q in range(1, 4):
                question = Question.objects.create(
                    passage=passage,
                    question_text=f"Question {q} for passage {i}?",
                    question_type=random.choice(question_types),
                    correct_answer="Option A",
                    score=1,
                )

                correct_option_index = random.randint(0, 3)

                for o in range(4):
                    Option.objects.create(
                        question=question,
                        text=f"Option {chr(65 + o)} for question {q} passage {i}",
                        is_correct=(o == correct_option_index),
                    )

        self.stdout.write(
            self.style.SUCCESS("✅ Successfully created 100 passages with questions and options")
        )
