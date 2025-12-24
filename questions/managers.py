from django.db import models
from django.db.models import Count

class ActiveCheck(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
class QuestionManager(models.Manager):
    def get_by_tag(self, tag_name: str):
        return self.get_queryset().filter(tags__name=tag_name, is_active=True).annotate(num_answers=Count("answer")).order_by("-created_at")
    
    def hot(self):
        return self.get_queryset().filter(is_active=True).annotate(num_answers=Count('answer')).order_by('-num_answers')

    def new(self):
        return self.get_queryset().filter(is_active=True).annotate(num_answers=Count('answer')).order_by('-created_at')
    
    def by_id(self, id: int):
        return self.get_queryset().filter(is_active=True, id=id).annotate(num_answers=Count('answer')).first()