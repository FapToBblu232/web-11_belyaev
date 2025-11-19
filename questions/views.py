from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random

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
def index_view(request):
    page = paginate(QUESTIONS, request)
    return render(request, "index.html", context={"page_obj": page, "question_list": page.object_list})

def question_view(request, pk):
    return render(request, "question.html", context={"question": QUESTIONS[pk], "answers": ANSWERS})

def hot_view(request):
    sorted_list = sorted(QUESTIONS, key=lambda x: x["likes"], reverse=True)
    page = paginate(sorted_list, request)
    return render(request, "index.html", context={"page_obj": page, "question_list": page.object_list})

def tag_view(request, tag):
    page = paginate(QUESTIONS, request)
    return render(request, "tag.html", context={"page_obj": page, "question_list": page.object_list, "tag": tag})

def login_view(request):
    return render(request, "login.html")

def signup_view(request):
    return render(request, "register.html")

def ask_view(request):
    return render(request, "new_question.html")

def settings_view(request):
    return render(request, "settings.html")