from django.contrib import admin
from . models import Chapter, Lesson, Profile, GuidesSupport, GuideSupportContent, LessonContent, HomePage, PracticeOption, PracticeQuestion
from rest_framework.authtoken.models import Token

# Register your models here.

class HomePageModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'description', 'image'
    )
admin.site.register(HomePage, HomePageModelAdmin)


class ChapterModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'name', 'description','created'
    )
admin.site.register(Chapter, ChapterModelAdmin)



class LessonModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'name', 'title', 'chapter', 'created', 'updated'
    )
admin.site.register(Lesson, LessonModelAdmin)



class LessonContentModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'lesson', 'image', 'description', 'glossary', 'video'
    )
admin.site.register(LessonContent, LessonContentModelAdmin)



# class QuestionModelAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'title', 'description', 'chapter', 'options', 'image'
#     )
# admin.site.register(Question, QuestionModelAdmin)



class ProfileModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'full_name', 'image', 'created_at'
    )
admin.site.register(Profile, ProfileModelAdmin)



class GuidesSupportModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'title', 'status', 'created'
    )
admin.site.register(GuidesSupport, GuidesSupportModelAdmin)


class GuideSupportContentModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'guide', 'image', 'description', 'video', 'created'
    )
admin.site.register(GuideSupportContent, GuideSupportContentModelAdmin)



class PracticeOptionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'question', 'text', 'is_correct'
    )
admin.site.register(PracticeOption, PracticeOptionAdmin)



class PracticeQuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'chapter', 'type', 'question_text', 'explanation', 'image', 'multiple_answers'
    )
admin.site.register(PracticeQuestion, PracticeQuestionAdmin)