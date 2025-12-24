import random
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.views.generic import FormView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from questions.forms import AnswerForm, AskForm, LoginForm, ProfileForm, SignupForm
from questions.models import Question, Answer, UserProfile
from django.db.models import Count
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

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


class QuestionView(View):
    def get(self, request, pk):
        question = Question.objects.by_id(pk)
        form = AnswerForm()
        return render(request, "question.html", {
            "question": question,
            "answers": question.answer_set.all(),
            "form": form
        })

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("/login/?continue=" + request.path)

        question = Question.objects.by_id(pk)
        form = AnswerForm(request.POST)

        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = question
            answer.save()
            return redirect(f"/question/{pk}/#answer-{answer.id}")

        return render(request, "question.html", {
            "question": question,
            "answers": question.answer_set.all(),
            "form": form
        })
    

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


class LoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm

    def form_valid(self, form):
        login(self.request, form.user)
        redirect_to = self.request.GET.get("continue", "/")
        return redirect(redirect_to)

class SignupView(FormView):
    template_name = "register.html"
    form_class = SignupForm

    def form_valid(self, form):
        user = form.save()
        UserProfile.objects.create(user=user, nickname=user.username, avatar="")
        login(self.request, user)
        return redirect("/")
    
def logout_view(request):
    logout(request)
    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def settings_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={"nickname": request.user.username, "avatar": ""}
    )
    
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("settings_view")

    return render(request, "settings.html", {"form": form})


@login_required
def ask_view(request):
    form = AskForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        q = form.save(commit=False)
        q.author = request.user
        q.save()
        form.save_m2m()
        return redirect("question_view", pk=q.id)

    return render(request, "new_question.html", {"form": form})