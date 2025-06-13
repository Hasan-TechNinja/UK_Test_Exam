from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100, default="Name")
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
    

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='theory_categories')
    name = models.CharField(max_length=100, default="")
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="")
    title = models.CharField(max_length=100)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created']


class LessonContent(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="lesson")
    description = models.TextField()
    glossary = models.TextField(max_length=200, default="")
    video = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.lesson.name



class Question(models.Model):
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=200, blank=True, null=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, blank=True, null=True)
    options = models.JSONField(default=" ")
    image = models.ImageField(upload_to="question", blank=True, null=True)

    def __str__(self):
        return self.title
    

class GuidesSupport(models.Model):
    name = models.CharField(max_length=150, default="")
    title = models.CharField(max_length=200)
    status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class GuideSupportContent(models.Model):
    guide = models.ForeignKey(GuidesSupport, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="GuidesAndSupport", blank=True, null=True)
    description = models.TextField(default=" ")
    video = models.URLField(blank=True)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.guide.name