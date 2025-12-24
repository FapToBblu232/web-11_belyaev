from django.urls import re_path, path

from questions.views import *

urlpatterns = [
    path("logout/", logout_view, name="logout"),
    path('question/<int:pk>/', QuestionView.as_view(), name="question_view"),
    path('hot/', HotView.as_view(), name="hot_view"),
    path('tag/<slug:tag>', TagView.as_view(), name="tag_view"),
    path('login/', LoginView.as_view(), name="login_view"),
    path('signup/', SignupView.as_view(), name="signup_view"),
    path('ask/', ask_view, name="ask_view"),
    path('settings/', settings_view, name="settings_view"),
    re_path(r'^', IndexView.as_view(), name="index_question_view"),
]
