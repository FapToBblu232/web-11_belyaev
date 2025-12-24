import random
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.views.generic import FormView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from questions.forms import AnswerForm, AskForm, LoginForm, ProfileForm, SignupForm
from questions.models import AnswerReaction, Question, Answer, QuestionReaction, UserProfile
from django.db.models import Count
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect


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
        question_list = page.object_list

        if self.request.user.is_authenticated:
            user_reactions = QuestionReaction.objects.filter(
                author=self.request.user, question__in=question_list
            ).values_list('question_id', 'is_like')
            reactions_dict = {qid: 'like' if is_like else 'dislike' for qid, is_like in user_reactions}
            for question in question_list:
                question.user_reaction = reactions_dict.get(question.id)

        context["page_obj"] = page
        context["question_list"] = page.object_list
        return context


class QuestionView(View):
    def get(self, request, pk):
        question = Question.objects.by_id(pk)
        form = AnswerForm()
        answers = list(question.answer_set.all())
        if request.user.is_authenticated:
            q_react = QuestionReaction.objects.filter(question=question, author=request.user).first()
            question.user_reaction = 'like' if q_react and q_react.is_like else 'dislike' if q_react else None
            for ans in answers:
                a_react = AnswerReaction.objects.filter(answer=ans, author=request.user).first()
                ans.user_reaction = 'like' if a_react and a_react.is_like else 'dislike' if a_react else None

        return render(request, "question.html", {
            "question": question,
            "answers": answers,
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
        question_list = page.object_list

        if self.request.user.is_authenticated:
            user_reactions = QuestionReaction.objects.filter(
                author=self.request.user, question__in=question_list
            ).values_list('question_id', 'is_like')
            reactions_dict = {qid: 'like' if is_like else 'dislike' for qid, is_like in user_reactions}
            for question in question_list:
                question.user_reaction = reactions_dict.get(question.id)

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
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.save()

        # Создаём профиль
        avatar_file = self.request.FILES.get("avatar")
        UserProfile.objects.create(
            user=user,
            nickname=user.username,
            avatar=avatar_file if avatar_file else ""
        )

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

    return render(request, "settings.html", {"form": form, "profile": profile})


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

@login_required
@require_POST
def question_react(request, pk):
    data = json.loads(request.body)
    question = Question.objects.get(pk=pk)
    reaction = QuestionReaction(question=question, author=request.user, is_like=data['is_like'])
    reaction.save()
    user_reaction = 'like' if reaction.is_like else 'dislike'
    return JsonResponse({
        'likes_count': question.likes_count,
        'dislikes_count': question.dislikes_count,
        'user_reaction': user_reaction
    })

@login_required
@require_POST
def answer_react(request, pk):
    data = json.loads(request.body)
    answer = Answer.objects.get(pk=pk)
    reaction = AnswerReaction(answer=answer, author=request.user, is_like=data['is_like'])
    reaction.save()
    user_reaction = 'like' if reaction.is_like else 'dislike'
    return JsonResponse({
        'likes_count': answer.likes_count,
        'dislikes_count': answer.dislikes_count,
        'user_reaction': user_reaction
    })

@login_required
@require_POST
def mark_correct_answer(request, pk):
    answer = Answer.objects.get(pk=pk)
    if request.user != answer.question.author:
        return JsonResponse({'status': 'error', 'error': 'Not allowed'}, status=403)
    # Сброс всех отметок
    answer.question.answer_set.update(is_correct=False)
    answer.is_correct = True
    answer.save(update_fields=['is_correct'])
    return JsonResponse({'status': 'ok'})