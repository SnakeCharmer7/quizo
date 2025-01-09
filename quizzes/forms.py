from django import forms
from .models import Quiz, Question, Answer
from django.forms import inlineformset_factory


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'category', 'is_public']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'image']


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
