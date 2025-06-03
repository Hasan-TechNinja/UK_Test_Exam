from django.contrib import admin
from . models import Chapter, Lesson, Question

# Register your models here.

# class UnitModelAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'user', 'name', 'description', 'image', 'created'
#     )
# admin.site.register(Unit, UnitModelAdmin)

# class LessonModelAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'user', 'title', 'description', 'unit', 'theory', 'structure', 'created', 'updated'
#     )
# admin.site.register(Lesson, LessonModelAdmin)


# class QuestionModelAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'text', 'audio', 'type', 'option'
#     )
# admin.site.register(Question, QuestionModelAdmin)