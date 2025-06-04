from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100, default="Name")
    app_language = models.CharField(max_length=20, default='en')  # e.g., 'en', 'fr', 'bn'
    listening_language = models.CharField(max_length=20, default='en')
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    font_size = models.CharField(max_length=10, choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')], default='medium')
    theme_mode = models.CharField(max_length=10, choices=[('light', 'Light'),('dark', 'Dark'),('system', 'System Default')], default='system')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Chapter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='theory_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=150)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, blank=True, null=True)
    theory = RichTextField()
    audio = models.CharField(max_length=300, blank=True, null=True) 
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} --- {self.user.username}"
    
    class Meta:
        ordering = ['-created']
        verbose_name = "Theory"
        verbose_name_plural = "Theories"


class Question(models.Model):
    title = models.CharField(max_length=150, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    option = models.JSONField()
    audio = models.CharField(max_length=150)
    image = models.ImageField(upload_to="question", blank=True, null=True)

    def __str__(self):
        return self.title