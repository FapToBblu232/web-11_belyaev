from django.core.management.base import BaseCommand
from questions.models import *
from django.contrib.auth.models import User
import random
import time
# from tqdm import tqdm 

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--ratio", dest="num", type=int, default=1)

    def handle(self, *args, **options):
        start = time.perf_counter()
        num = options["num"]
        random_part = random.randint(1,100)
        num_users = num
        num_tags = num
        num_questions = num * 10
        num_answers = num * 100

        BATCH_SIZE = 5000

        QuestionReaction.disable_reaction_updates = True
        AnswerReaction.disable_reaction_updates = True

        self.stdout.write(f"Creating {num_users} users...")
        users = [User(username=f"user_{i}_{random_part}", password="123") for i in range(num_users)]
        User.objects.bulk_create(users, batch_size=BATCH_SIZE)
        users = list(User.objects.all())
        self.stdout.write(self.style.SUCCESS("Users created."))
    
        self.stdout.write(f"Creating {num_tags} tags...")
        tags = [Tag(name=f"tag_{i}_{random_part}") for i in range(num_tags)]
        Tag.objects.bulk_create(tags, batch_size=BATCH_SIZE)
        tags = list(Tag.objects.all())
        self.stdout.write(self.style.SUCCESS("Tags created."))


        self.stdout.write(f"Creating {num_questions} questions...")
        questions = [Question(
            title=f"Question {i}{random_part}",
            content="Lorem ipsum dolor sit amet lorem",
            author=random.choice(users),
        ) for i in range(num_questions)]
        Question.objects.bulk_create(questions, batch_size=BATCH_SIZE)

        questions = list(Question.objects.all())

        m2m_relations = []
        through_model = Question.tags.through
        for q in questions:
            selected_tags = random.sample(tags, k=min(len(tags), random.randint(1, 3)))
            for t in selected_tags:
                m2m_relations.append(through_model(question_id=q.id, tag_id=t.id))
        through_model.objects.bulk_create(m2m_relations, batch_size=BATCH_SIZE)

        self.stdout.write(f"Generating reactions for questions...")
        question_reactions = []
        for q in questions:
            likes = random.randint(0, 12)
            dislikes = random.randint(0, 7)
            reactors = random.sample([u for u in users if u != q.author], k=min(likes + dislikes, len(users) - 1))

            for idx, u in enumerate(reactors):
                question_reactions.append(QuestionReaction(
                    question=q,
                    author=u,
                    is_like=idx < likes
                ))

            q.likes_count = likes
            q.dislikes_count = dislikes

        Question.objects.bulk_update(questions, ['likes_count', 'dislikes_count'], batch_size=BATCH_SIZE)
        QuestionReaction.objects.bulk_create(question_reactions, batch_size=BATCH_SIZE)
        self.stdout.write(self.style.SUCCESS("Questions and reactions created."))

        self.stdout.write(f"Creating {num_answers} answers...")
        answers = [Answer(
            question=random.choice(questions),
            content="Answer text",
            author=random.choice(users)
        ) for _ in range(num_answers)]
        Answer.objects.bulk_create(answers, batch_size=BATCH_SIZE)
        answers = list(Answer.objects.all())

        answer_reactions = []
        for a in answers:
            likes = random.randint(0, 2)
            dislikes = random.randint(0, 2)
            reactors = random.sample([u for u in users if u != a.author], k=min(likes + dislikes, len(users) - 1))

            for idx, u in enumerate(reactors):
                answer_reactions.append(AnswerReaction(
                    answer=a,
                    author=u,
                    is_like=idx < likes
                ))

            a.likes_count = likes
            a.dislikes_count = dislikes

        Answer.objects.bulk_update(answers, ['likes_count', 'dislikes_count'], batch_size=BATCH_SIZE)
        AnswerReaction.objects.bulk_create(answer_reactions, batch_size=BATCH_SIZE)
        self.stdout.write(self.style.SUCCESS("Answers and reactions created."))

        end = time.perf_counter()
        QuestionReaction.disable_reaction_updates = False
        AnswerReaction.disable_reaction_updates = False
        print(f"Завершено за {end - start:.2f} секунд")