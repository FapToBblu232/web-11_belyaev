from django.urls import re_path, path

from questions.views import ask_view, hot_view, index_view, login_view, question_view, settings_view, signup_view, tag_view

urlpatterns = [
    path('question/<int:pk>/', question_view, name="question_view"),
    path('hot/', hot_view, name="hot_view"),
    path('tag/<slug:tag>', tag_view, name="tag_view"),
    path('login/', login_view, name="login_view"),
    path('signup/', signup_view, name="signup_view"),
    path('ask/', ask_view, name="ask_view"),
    path('settings/', settings_view, name="settings_view"),
    re_path(r'^', index_view, name="index_question_view"),
]
