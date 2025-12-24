from django.contrib import admin

from questions.models import Answer, AnswerReaction, Question, QuestionReaction, Tag, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    ...

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    ...

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    ...

@admin.register(AnswerReaction)
class AnswerReactionAdmin(admin.ModelAdmin):
    ...

@admin.register(QuestionReaction)
class QuestionReactionAdmin(admin.ModelAdmin):
    ...

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    ...
# Register your models here.
