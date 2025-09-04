from django.db import models
# from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
# from django.core.validators import MaxValueValidator, MinValueValidator
import uuid
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import json

# Create your models here.


User = get_user_model()
class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100, default="Name")
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
    

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)



LeftMockTest = [
    ('Limited', 'Limited'),
    ('Unlimited', 'Unlimited'),
]

class UserEvaluation(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    MockTestTaken = models.PositiveIntegerField(default=0)
    LeftMockTest = models.CharField(max_length=20, choices=LeftMockTest, default='Limited')
    PracticeCompleted = models.CharField(max_length=100)
    QuestionAnswered = models.CharField(max_length=100)
    CorrectAnswered = models.CharField(max_length=100)
    WrongAnswered = models.CharField(max_length=100)

    def __str__(self):
        return f"Evaluation of {self.user.full_name}"
    
    

class HomePage(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=200)
    image = models.ImageField(upload_to="home")

    def __str__(self):
        return self.title


class Chapter(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='theory_categories')
    name = models.CharField(max_length=100, default="")
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="")
    title = models.CharField(max_length=100)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
    # updated = models.DateTimeField(auto_now=True)
    # status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.chapter.name} - {self.name}"
    
    class Meta:
        ordering = ['-created']
    
    
class LessonContent(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="lesson")
    description = models.TextField()
    glossary = models.JSONField(default=list)  # ✅ cleaner
    video = models.URLField(blank=True, null=True)



class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    completed_contents = models.ManyToManyField(LessonContent, blank=True)
    completion_percentage = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.name} ({self.completion_percentage}%)"

    def update_completion(self):
        total = self.lesson.lessoncontent_set.count()
        completed = self.completed_contents.count()
        self.completion_percentage = (completed / total * 100) if total else 0.0
        self.save()
    


class GuidesSupport(models.Model):
    name = models.CharField(max_length=150, default="")
    title = models.CharField(max_length=200)
    # status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class GuideSupportContent(models.Model):
    guide = models.ForeignKey(GuidesSupport, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="GuidesAndSupport", blank=True, null=True)
    description = models.TextField(default=" ")
    glossary = models.TextField(default=list, blank=True)
    video = models.URLField(blank=True)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.guide.name

    def get_glossary_string_list(self, delimiter=','):
        """
        Return glossary as a list. Handles:
          - JSON-encoded strings like '["as","second"]'
          - Plain comma-separated strings like 'as, second'
        """
        raw = (self.glossary or "").strip()
        if not raw:
            return []
        # Try JSON first
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except json.JSONDecodeError:
            pass
        # Fallback: CSV-style
        return [item.strip() for item in raw.split(delimiter) if item.strip()]

    def set_glossary_string_list(self, data_list, delimiter=','):
        """
        Accept a list (or a JSON string) and store consistently as comma-separated,
        OR switch to JSONField later (recommended).
        """
        # If caller accidentally passes a JSON string, normalize it
        if isinstance(data_list, str):
            try:
                maybe_list = json.loads(data_list)
                if isinstance(maybe_list, list):
                    data_list = maybe_list
            except json.JSONDecodeError:
                # Treat the string as CSV
                data_list = [x.strip() for x in data_list.split(delimiter)]
        self.glossary = delimiter.join([str(x).strip() for x in data_list if str(x).strip()])



QuestionType = {
    "practice": "practice",
    "mockTest": "mockTest",
    "freeMockTest": "freeMockTest",
}
    

class Question(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='questions')
    type = models.CharField(choices=QuestionType, max_length=50, default="practice")
    question_text = models.TextField()
    explanation = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='questions/', blank=True, null=True)
    multiple_answers = models.BooleanField(default=True)

    def __str__(self):
        return self.question_text
    

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        # return f"{self.question.id, self.text}"
        return f"Q{self.question.id}: {self.text}"
        # return f"Q{self.question.id} - {self.question.question_text[:40]}...: {self.text}"
    
class ChapterProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chapter_progress')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='progress')
    completed_questions = models.ManyToManyField(Question, blank=True)
    completion_percentage = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('user', 'chapter')  # One progress entry per user per chapter

    def __str__(self):
        return f"{self.user.username} - {self.chapter.name} ({self.completion_percentage}%)"

    def update_completion(self):
        total_questions = self.chapter.questions.filter(type="practice").count()
        completed = self.completed_questions.filter(type="practice").count()
        self.completion_percentage = (completed / total_questions * 100) if total_questions else 0.0
        self.save()


class MockTestSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    total_questions = models.IntegerField(default=24)
    duration_minutes = models.IntegerField(default=45)

    def is_passed(self):
        return self.score is not None and self.score >= 70

class MockTestAnswer(models.Model):
    session = models.ForeignKey(MockTestSession, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(QuestionOption)
    is_correct = models.BooleanField(default=False)
    
    
class FreeMockTestSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    total_questions = models.IntegerField(default=24)
    duration_minutes = models.IntegerField(default=45)

    def is_passed(self):
        return self.score is not None and self.score >= 70

class FreeMockTestAnswer(models.Model):
    session = models.ForeignKey(FreeMockTestSession, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(QuestionOption)
    is_correct = models.BooleanField(default=False)
