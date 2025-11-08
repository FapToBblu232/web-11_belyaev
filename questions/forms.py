from django import forms

class QuestionSerializer(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('id', 'text', 'description')