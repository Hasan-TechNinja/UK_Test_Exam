from django.db import models
from tinymce.models import HTMLField
from django.contrib.auth.models import User

# Create your models here.


class TheoryCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Theory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = HTMLField()
    category = models.ForeignKey(TheoryCategory, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} --- {self.user.username}"
    
    class Meta:
        ordering = ['-created']