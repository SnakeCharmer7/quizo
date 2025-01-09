from django.views import View, generic
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.forms import formset_factory
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from .models import Quiz, Question, Answer, QuizResult
from .forms import QuizForm, QuestionForm, AnswerForm


class QuizListView(generic.ListView):
    model = Quiz
    template_name = "quizzes/quiz_list.html"
    context_object_name = "quizzes"

    def get_queryset(self):
        user = self.request.user.id
        return Quiz.objects.filter(Q(is_public=True) | Q(author=user))


class QuizSolveView(LoginRequiredMixin, generic.DetailView):
    model = Quiz
    template_name = "quizzes/quiz_solve.html"
    context_object_name = "quiz"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['questions'] = self.object.questions.all()
    #     return context


class QuizResultView(View):
    def get(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)

        try:
            result = QuizResult.objects.filter(user=request.user, quiz=quiz).latest('completed_at')
        except ObjectDoesNotExist:
            result = None

        percentage = (result.score / result.total_questions) * 100

        return render(request, 'quizzes/quiz_result.html', {
            'quiz': quiz,
            'score': result.score,
            'total_questions': result.total_questions,
            'percentage': percentage,
        })


class QuizSubmitView(View):
    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        questions = quiz.questions.all()
        score = 0
        total_questions = quiz.questions.count()

        for question in questions:      
            user_answer_ids = request.POST.getlist(f'question-{question.id}')
            correct_answers = question.answers.filter(is_correct=True)

            # Sprawdź, czy wszystkie poprawne odpowiedzi zostały wybrane
            correct_ids = set(correct_answers.values_list('id', flat=True))
            user_ids = set(map(int, user_answer_ids))  # Zamień odpowiedzi użytkownika na zestaw int

            if user_ids == correct_ids:  # Sprawdź, czy odpowiedzi użytkownika są poprawne
                score += 1

        QuizResult.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            total_questions=total_questions,
        )

        return redirect('quiz_result', pk=quiz.pk)


class QuizCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = QuizForm()
        return render(request, 'quizzes/quiz_create.html', {'form': form})

    def post(self, request):
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.author = request.user
            quiz.save()
            return redirect('quiz_add_question', pk=quiz.pk)
        return render(request, 'quizzes/quiz_create.html', {'form': form})


class QuestionAddView(LoginRequiredMixin, View):
    def get(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        question_form = QuestionForm()
        AnswerFormSet = formset_factory(AnswerForm, extra=2)
        answer_formset = AnswerFormSet()

        return render(request, 'quizzes/question_add.html', {
            'quiz': quiz,
            'question_form': question_form,
            'answer_forms': answer_formset,
            'form_count': len(answer_formset),
        })

    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        question_form = QuestionForm(request.POST)
        AnswerFormSet = formset_factory(AnswerForm)
        answer_formset = AnswerFormSet(request.POST)

        if question_form.is_valid() and answer_formset.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()

            for form in answer_formset:
                answer = form.save(commit=False)
                answer.question = question
                answer.save()

            if "add_question" in request.POST:
                return redirect('quiz_add_question', pk=quiz.pk)
            elif "save" in request.POST:
                return redirect('quiz_list')

        return render(request, 'quizzes/quiz_list.html', {
            'quiz': quiz,
            'question_form': question_form,
            'answer_forms': answer_formset,
            'form_count': len(answer_formset),
        })


class QuizUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = "quizzes/quiz_form.html"

    def get_queryset(self):
        return Quiz.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('quiz_list')


class QuizDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Quiz
    template_name = "quizzes/quiz_confirm_delete.html"
    success_url = reverse_lazy('quiz_list')

    def get_queryset(self):
        return Quiz.objects.filter(author=self.request.user)


class SingUpView(generic.CreateView):
    template_name = "quizzes/register.html"
    success_url = reverse_lazy('login')
    form_class = UserCreationForm