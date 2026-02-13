import random
from django.core.management.base import BaseCommand
from faker import Faker

from team14.models import Passage, Question, Option


fake = Faker()


DIFFICULTY_CHOICES = ['easy', 'medium', 'hard']
TOPIC_CHOICES = ['biology', 'history', 'astronomy', 'geology', 'anthropology']

QUESTION_TYPES = [
    'factual',
    'negative_factual',
    'inference',
    'vocabulary',
]


DIFFICULTY_LENGTH_MAP = {
    'easy': (120, 180),
    'medium': (200, 280),
    'hard': (320, 450),
}


TOPIC_KEYWORDS = {
    'biology': ['cells', 'organisms', 'photosynthesis', 'evolution'],
    'history': ['civilization', 'empire', 'revolution', 'trade'],
    'astronomy': ['planets', 'stars', 'galaxies', 'orbit'],
    'geology': ['earthquake', 'minerals', 'volcano', 'crust'],
    'anthropology': ['culture', 'society', 'rituals', 'migration'],
}


class Command(BaseCommand):
    help = "Seed database with TOEFL-style realistic passages using Faker"

    def handle(self, *args, **kwargs):
        #Passage.objects.all().delete()

        for i in range(1, 101):
            difficulty = random.choice(DIFFICULTY_CHOICES)
            topic = random.choice(TOPIC_CHOICES)

            min_len, max_len = DIFFICULTY_LENGTH_MAP[difficulty]
            target_length = random.randint(min_len, max_len)

            paragraphs = []
            word_count = 0

            while word_count < target_length:
                paragraph = fake.paragraph(nb_sentences=5)
                paragraphs.append(paragraph)
                word_count += len(paragraph.split())

            text = "\n\n".join(paragraphs)

            passage = Passage.objects.create(
                title=fake.sentence(nb_words=6),
                text=text,
                topic=topic,
                difficulty_level=difficulty,
                text_length=len(text.split()),
                rubric_version="toefl-reading-v2",
                version=1,
            )

            # 3–5 سوال برای هر Passage
            for _ in range(random.randint(3, 5)):
                q_type = random.choice(QUESTION_TYPES)

                keyword = random.choice(TOPIC_KEYWORDS[topic])

                question = Question.objects.create(
                    passage=passage,
                    question_text=f"What does the passage suggest about {keyword}?",
                    question_type=q_type,
                    correct_answer="",
                    score=1,
                )

                correct_index = random.randint(0, 3)

                for idx in range(4):
                    option_text = fake.sentence(nb_words=10)
                    is_correct = idx == correct_index

                    Option.objects.create(
                        question=question,
                        text=option_text,
                        is_correct=is_correct,
                    )

                    if is_correct:
                        question.correct_answer = option_text

                question.save()

        self.stdout.write(
            self.style.SUCCESS("✅ 100 TOEFL-style passages generated successfully")
        )
