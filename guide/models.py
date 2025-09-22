from django.db import models
from django.contrib.auth.models import User


class GuideChapter(models.Model):
    name = models.CharField(max_length=100, default="")
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GuideLesson(models.Model):
    name = models.CharField(max_length=100, default="")
    title = models.CharField(max_length=100)
    chapter = models.ForeignKey(
        GuideChapter, on_delete=models.CASCADE, related_name="lessons"
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chapter.name} - {self.name}"

    class Meta:
        ordering = ["-created"]


class GuideLessonContent(models.Model):
    lesson = models.ForeignKey(
        GuideLesson, on_delete=models.CASCADE, related_name="contents"
    )
    image = models.ImageField(upload_to="lesson")
    description = models.TextField()
    video = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.lesson.title} - Content"


class GuideGlossary(models.Model):
    lesson_content = models.ForeignKey(
        GuideLessonContent, on_delete=models.CASCADE, related_name="glossaries"
    )
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)

    class Meta:
        verbose_name_plural = "Glossaries"

    def __str__(self):
        return self.title


class GuideLessonProgress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="guide_lesson_progress"
    )
    lesson = models.ForeignKey(
        GuideLesson, on_delete=models.CASCADE, related_name="progress_records"
    )
    completed_contents = models.ManyToManyField(GuideLessonContent, blank=True)
    completion_percentage = models.FloatField(default=0.0)

    class Meta:
        unique_together = ("user", "lesson")

    def __str__(self):
        return f"{self.user.username} - {self.lesson.name} ({self.completion_percentage:.2f}%)"

    def update_completion(self):
        total = self.lesson.contents.count()  # ✅ fixed related_name
        completed = self.completed_contents.count()
        self.completion_percentage = (completed / total * 100) if total else 0.0
        self.save()
