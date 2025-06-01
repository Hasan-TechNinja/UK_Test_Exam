from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User

# Create your models here.

class Unit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='theory_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='unit')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=150)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    theory = RichTextField()
    structure = models.JSONField() 
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} --- {self.user.username}"
    
    class Meta:
        ordering = ['-created']
        verbose_name = "Theory"
        verbose_name_plural = "Theories"


class Question(models.Model):
    text = models.CharField(max_length=150)
    audio = models.CharField(max_length=150)
    type = models.TextField()
    option = models.JSONField()

    def __str__(self):
        return self.text