from django.contrib import admin
from . models import Chapter, Lesson, Profile, GuidesSupport, GuideSupportContent, LessonContent, HomePage, QuestionOption, Question, UserEvaluation
from rest_framework.authtoken.models import Token

# Register your models here.

class HomePageModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'description', 'image'
    )
admin.site.register(HomePage, HomePageModelAdmin)


class ChapterModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'description','created'
    )
admin.site.register(Chapter, ChapterModelAdmin)



class LessonModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'title', 'chapter', 'created',
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


class UserEvaluationModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'MockTestTaken', 'LeftMockTest', 'PracticeCompleted', 'QuestionAnswered', 'CorrectAnswered', 'WrongAnswered'
    )
admin.site.register(UserEvaluation, UserEvaluationModelAdmin)



class GuidesSupportModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'title', 'created'
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
admin.site.register(QuestionOption, PracticeOptionAdmin)



class PracticeQuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'chapter', 'type', 'question_text', 'explanation', 'image', 'multiple_answers'
    )
admin.site.register(Question, PracticeQuestionAdmin)