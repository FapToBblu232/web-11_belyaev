from django.db import models
from django.contrib.auth.models import User

# from gramm.managers import DefaultManager, PostManager
from questions.managers import ActiveCheck, QuestionManager

# Create your models here.

class UserProfile(models.Model):
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    nickname = models.CharField(verbose_name="Никнейм пользователя", max_length=255)
    user = models.OneToOneField(User, verbose_name="Пользователь", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} / Профиль пользователя {self.user}"
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователя"


class DefaultContentModel(models.Model):
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата последнего обновления", auto_now=True)

    likes_count = models.IntegerField(verbose_name="Количество лайков", default=0)
    dislikes_count = models.IntegerField(verbose_name="Количество дизлайков", default=0)

    is_active = models.BooleanField(verbose_name="Активно ли?", help_text="Видно ли пользователям?", default=True)

    active = ActiveCheck()
    objects = QuestionManager()

    class Meta:
        abstract = True


class Question(DefaultContentModel):
    title = models.CharField(verbose_name="Заголовок", max_length=400)
    content = models.TextField(verbose_name="Контент вопроса", max_length=4000)
    author = models.ForeignKey(User, verbose_name="Автор", on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField("questions.Tag", verbose_name="Все тэги", blank=True)

    def __str__(self):
        return f"{self.id} / {self.title} от {self.author}"

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Answer(DefaultContentModel):
    question = models.ForeignKey("questions.Question", verbose_name="Родительский вопрос", on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Контент ответа", max_length=4000)
    author = models.ForeignKey(User, verbose_name="Автор", on_delete=models.SET_NULL, null=True)
    parent_answer = models.ForeignKey("questions.Answer", verbose_name="Корневой ответ", null=True, blank=True, default=None, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    
    def __str__(self):
        return f"{self.id} / Ответ на вопрос {self.question} от {self.author}"
    
    class Meta:
        verbose_name = "Ответ на вопрос"
        verbose_name_plural = "Ответы на вопросы"


class ReactiomDefaultModel(models.Model):
    author = models.ForeignKey(User, verbose_name="Кто поставил", on_delete=models.CASCADE)
    is_like = models.BooleanField(verbose_name="Лайк ли это?")

    class Meta:
        abstract = True


class AnswerReaction(ReactiomDefaultModel):
    disable_reaction_updates = False

    answer = models.ForeignKey("questions.Answer", verbose_name="Родительский ответ", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.id} / Реакция от {self.author} на ответ"
    
    class Meta:
        verbose_name = "Лайк к ответу"
        verbose_name_plural = "Лайки к ответу"
        # unique_together = ['answer', 'author']

    # Не знаю, насколько это правильно, но я решил убрать unique_together,
    # т.к. в админке не работала моя логика "если есть, то нужно обновить".
    def save(self, *args, **kwargs):
        if getattr(self, "disable_reaction_updates", False):
            return super().save(*args, **kwargs)
        
        existing = AnswerReaction.objects.filter(
            answer=self.answer,
            author=self.author
        ).first()

        # Если уже есть такая реакция - просто обновляем
        # пар вида null - пользователь быть не должно, т.к. при удалении пользователя лайк удаляется
        if existing:
        # если реакция уже есть и тип реакции изменился
            if existing.is_like != self.is_like:
                if existing.is_like:
                    self.answer.likes_count -= 1
                    self.answer.dislikes_count += 1
                else:
                    self.answer.likes_count += 1
                    self.answer.dislikes_count -= 1

                existing.disable_reaction_updates = True
                existing.is_like = self.is_like
                existing.save(update_fields=['is_like'])
                self.answer.save(update_fields=['likes_count', 'dislikes_count'])
            # просто возвращаем существующую запись, не создавая новую
            self.pk = existing.pk
        else:
            # новая реакция
            if self.is_like:
                self.answer.likes_count += 1
            else:
                self.answer.dislikes_count += 1
            self.answer.save(update_fields=['likes_count', 'dislikes_count'])
            super().save(*args, **kwargs)


class QuestionReaction(ReactiomDefaultModel):
    disable_reaction_updates = False

    question = models.ForeignKey("questions.Question", verbose_name="Родительский вопрос", on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return f"{self.id} / Реакция от {self.author} на вопрос"
    
    class Meta:
        verbose_name = "Лайк к вопросу"
        verbose_name_plural = "Лайки к вопросу"
        # unique_together = ['question', 'author']

    def save(self, *args, **kwargs):
        if getattr(self, "disable_reaction_updates", False):
            return super().save(*args, **kwargs)
        
        existing = QuestionReaction.objects.filter(
            question=self.question,
            author=self.author
        ).first()

        if existing:
        # если пользователь уже ставил реакцию, но тип изменился
            if existing.is_like != self.is_like:
                if existing.is_like:
                    self.question.likes_count -= 1
                    self.question.dislikes_count += 1
                else:
                    self.question.likes_count += 1
                    self.question.dislikes_count -= 1

                existing.disable_reaction_updates = True
                existing.is_like = self.is_like
                existing.save(update_fields=['is_like'])
                self.question.save(update_fields=['likes_count', 'dislikes_count'])
            # не создаём новую запись
            self.pk = existing.pk
        else:
            # новая реакция
            if self.is_like:
                self.question.likes_count += 1
            else:
                self.question.dislikes_count += 1

            self.question.save(update_fields=['likes_count', 'dislikes_count'])
            super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(verbose_name="Название тэга", max_length=50)

    def __str__(self):
        return f"{self.id} / Тэг \"{self.name}\""
    
    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"