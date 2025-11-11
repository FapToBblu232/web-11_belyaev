from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
from questions.models import Question, Answer
from django.db.models import Count

QUESTIONS = []
for i in range(61):
    QUESTIONS.append({
        "id": i,
        "text": "How to build a moon park?",
        "description" : "Lorem ipsum dolor sit amet consectetur adipisicing elit. Voluptates nesciunt vero reprehenderit iusto voluptatibus neque et, illum numquam impedit omnis, aperiam dolore, totam quis amet fugiat? Suscipit laboriosam animi alias!",
        "likes": random.randint(1, 100),
                      })


ANSWERS = []
for i in range(5):
    ANSWERS.append(
        {
            "id": i,
            "description" : "Lorem ipsum dolor sit amet consectetur adipisicing elit. Voluptates nesciunt vero reprehenderit iusto voluptatibus neque et, illum numquam impedit omnis, aperiam dolore, totam quis amet fugiat? Suscipit laboriosam animi alias!",
            "likes": random.randint(1, 100),
        }
    )

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        # если не число -> показываем первую страницу, тут, кста, должна пройти и пустая 
        page = paginator.page(1)
    except EmptyPage:
        # page_number > abs -> последнюю
        page = paginator.page(paginator.num_pages)
    return page

# Create your views here.
class IndexView(TemplateView):
    template_name = "index.html"

    #Question.active.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = Question.objects.new()
        page = paginate(questions, self.request)
        context["page_obj"] = page
        context["question_list"] = page.object_list
        return context


class QuestionView(TemplateView):
    template_name = "question.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = kwargs.get("pk")
        question = Question.objects.by_id(pk)

        context["question"] = question
        context["answers"] = question.answer_set.all()
        return context


class HotView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = Question.objects.hot()
        page = paginate(questions, self.request)
        context["page_obj"] = page
        context["question_list"] = page.object_list
        return context


class TagView(TemplateView):
    """Вопросы по тегу"""
    template_name = "tag.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = kwargs.get("tag")
        questions = Question.objects.get_by_tag(tag)
        page = paginate(questions, self.request)
        context["page_obj"] = page
        context["question_list"] = page.object_list
        context["tag"] = tag
        return context


class LoginView(TemplateView):
    template_name = "login.html"


class SignupView(TemplateView):
    template_name = "register.html"


class AskView(TemplateView):
    template_name = "new_question.html"


class SettingsView(TemplateView):
    template_name = "settings.html"