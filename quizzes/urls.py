from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.QuizListView.as_view(), name="quiz_list"),
    path('quiz/<int:pk>', views.QuizSolveView.as_view(), name="quiz_solve"),
    path('quiz/<int:pk>/submit/', views.QuizSubmitView.as_view(), name='quiz_submit'),
    path('quiz/<int:pk>/result/', views.QuizResultView.as_view(), name='quiz_result'),
    path('quiz/create/', views.QuizCreateView.as_view(), name="quiz_create"),
    path('quiz/<int:pk>/add_question', views.QuestionAddView.as_view(), name="quiz_add_question"),
    path('login/', auth_views.LoginView.as_view(template_name='quizzes/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.SingUpView.as_view(), name='register'),
]