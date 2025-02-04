from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Quiz, Question, Answer, Category
from .forms import CustomUserCreationForm, QuizForm


### TESTING MODELS
class QuizModelTest(TestCase):
    def setUp(self):
        """Creating user and quiz to test"""
        self.category = Category.objects.create(name="Nauka")
        self.user = User.objects.create(username="testuser")
        self.quiz = Quiz.objects.create(
            title="Test Quiz",
            description="Opis testowego quizu",
            category=self.category,
            author=self.user
        )

    def test_quiz_creation(self):
        self.assertEqual(self.quiz.title, "Test Quiz")
        self.assertEqual(self.quiz.author.username, "testuser")
        self.assertTrue(self.quiz.is_public)

class QuestionModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Nauka")
        self.user = User.objects.create(username="testuser")
        self.quiz = Quiz.objects.create(title="Quiz1", 
            description="Testowy quiz", 
            category=self.category,
            author=self.user
        )
        self.question = Question.objects.create(text="Jakie jest 2+2?", quiz=self.quiz)

    def test_question_creation(self):
        self.assertEqual(self.question.text, "Jakie jest 2+2?")
        self.assertEqual(self.question.quiz.title, "Quiz1")

class AnswerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.category = Category.objects.create(name="Nauka")
        self.quiz = Quiz.objects.create(title="Quiz1", 
            description="Testowy quiz", 
            category=self.category,
            author=self.user
        )
        self.question = Question.objects.create(text="Jakie jest 2+2?", quiz=self.quiz)
        self.answer = Answer.objects.create(text="4", is_correct=True, question=self.question)

    def test_answer_creation(self):
        self.assertEqual(self.answer.text, "4")
        self.assertTrue(self.answer.is_correct)
        self.assertEqual(self.answer.question.text, "Jakie jest 2+2?")


### TESTING VIEWS
class QuizViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.category = Category.objects.create(name="Nauka")
        self.quiz = Quiz.objects.create(title="Testowy Quiz", 
            description="Opis quizu", 
            category=self.category,
            author=self.user
        )

    def test_quiz_list_view(self):
        response = self.client.get(reverse("quiz_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Testowy Quiz")

    def test_quiz_create_view(self):
        self.client.login(username="testuser", password="testpassword")
        category = Category.objects.create(name="Matematyka")

        response = self.client.post(reverse("quiz_create"), {
            "title": "Nowy Quiz",
            "description": "Opis nowego quizu",
            "category": category.id,
            "is_public": True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Quiz.objects.filter(title="Nowy Quiz").exists())


### TESTING FORMS
class QuizFormTest(TestCase):
    def test_valid_form(self):
        """Test valid form"""
        self.category = Category.objects.create(name="Nauka")
        form_data = {"title": "Nowy Quiz", "description": "Opis quizu", "category": self.category, "is_public": True}
        form = QuizForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        """Test form without title"""
        form_data = {"title": "", "description": "Opis quizu", "category": "Nauka", "is_public": True}
        form = QuizForm(data=form_data)
        self.assertFalse(form.is_valid())

class RegistrationFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'username': 'valid_user',
            'password': 'Valid123',
            'password_confirm': 'Valid123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_username_too_short(self):
        form_data = {
            'username': 'short',
            'password': 'Valid123!',
            'password_confirm': 'Valid123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'][0], "Username must be at least 8 characters long.")

    def test_username_too_long(self):
        form_data = {
            'username': 'a' * 21,
            'password': 'Valid123!',
            'password_confirm': 'Valid123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'][0], "Username must contain a maximum of 20 characters.")

    def test_username_invalid_characters(self):
        form_data = {
            'username': 'invalid@user!',
            'password': 'Valid123!',
            'password_confirm': 'Valid123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'][0], "Username can only contain letters, numbers, underscores, and hyphens.")

    def test_password_missing_uppercase(self):
        form_data = {
            'username': 'validuser',
            'password': 'valid123!',
            'password_confirm': 'valid123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        self.assertEqual(form.errors['password'][0], "Password must contain at least one uppercase letter.")

    def test_password_missing_lowercase(self):
        form_data = {
            'username': 'validuser',
            'password': 'VALID123!',
            'password_confirm': 'VALID123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        self.assertEqual(form.errors['password'][0], "Password must contain at least one lowercase letter.")

    def test_password_missing_number(self):
        form_data = {
            'username': 'validuser',
            'password': 'ValidPassword!',
            'password_confirm': 'ValidPassword!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        self.assertEqual(form.errors['password'][0], "Password must contain at least one number.")

    def test_password_mismatch(self):
        form_data = {
            'username': 'validuser',
            'password': 'Valid123!',
            'password_confirm': 'Different123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password_confirm', form.errors)
        self.assertEqual(form.errors['password_confirm'][0], "Passwords must be the same.")

    def test_save_creates_user(self):
        form_data = {
            'username': 'validuser',
            'password': 'Valid123!',
            'password_confirm': 'Valid123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertIsInstance(user, User)
        self.assertTrue(user.check_password('Valid123!'))
