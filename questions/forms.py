from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from questions.models import Answer, Question, UserProfile

class QuestionSerializer(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('id', 'title', 'content')

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        user = authenticate(
            username=cleaned.get("username"),
            password=cleaned.get("password")
        )
        if not user:
            raise forms.ValidationError("Неверный логин или пароль")
        self.user = user
        return cleaned
    
class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password_confirmation = forms.CharField(widget=forms.PasswordInput, label="Repeat Password")
    class Meta:
        model = User
        fields = ("username", "email")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError("Passwords do not match!")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            UserProfile.objects.create(user=user)
        return user
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("nickname", "avatar")

class AskForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ("title", "content", "tags")

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("content",)