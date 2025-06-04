from django.contrib import admin
from . models import Chapter, Lesson, Question, Profile

# Register your models here.

class ChapterModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'name', 'description','created'
    )
admin.site.register(Chapter, ChapterModelAdmin)

class LessonModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'title', 'description', 'chapter', 'theory', 'audio', 'created', 'updated'
    )
admin.site.register(Lesson, LessonModelAdmin)


class QuestionModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'description', 'option', 'audio', 'image'
    )
admin.site.register(Question, QuestionModelAdmin)


class ProfileModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'full_name', 'app_language', 'listening_language', 'image', 'font_size', 'theme_mode', 'created_at'
    )
admin.site.register(Profile, ProfileModelAdmin)