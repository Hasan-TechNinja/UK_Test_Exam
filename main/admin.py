from django.contrib import admin
from . models import Chapter, Lesson, Profile, GuidesSupport, GuideSupportContent, LessonContent, HomePage, QuestionOption, Question, UserEvaluation, MockTestAnswer, MockTestSession, FreeMockTestSession, FreeMockTestAnswer, ChapterProgress, LessonProgress
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
    list_filter = ('chapter',)
admin.site.register(Lesson, LessonModelAdmin)



class LessonProgressAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'lesson', 'completion_percentage'
    )
admin.site.register(LessonProgress, LessonProgressAdmin)


class LessonContentModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'image', 'description', 'glossary', 'video')
    list_select_related = ('lesson', 'lesson__chapter')
    list_filter = ('lesson', 'lesson__chapter')
admin.site.register(LessonContent, LessonContentModelAdmin)


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



class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'text', 'is_correct')
    list_filter = ('question', 'is_correct')
    search_fields = ('question__question_text', 'text')
admin.site.register(QuestionOption, QuestionOptionAdmin)



class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'chapter', 'type', 'question_text', 'explanation', 'image', 'multiple_answers'
    )
    list_filter = ['type']
admin.site.register(Question, QuestionAdmin)



class MockTestSessionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'started_at', 'finished_at', 'score', 'total_questions', 'duration_minutes', 
    )
admin.site.register(MockTestSession, MockTestSessionAdmin)



class MockTestAnswerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'session', 'question', 'is_correct'
    )
admin.site.register(MockTestAnswer, MockTestAnswerAdmin)



class FreeMockTestSessionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'started_at', 'finished_at', 'score', 'total_questions', 'duration_minutes', 
    )
admin.site.register(FreeMockTestSession, FreeMockTestSessionAdmin)



class FreeMockTestAnswerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'session', 'question', 'is_correct'
    )
admin.site.register(FreeMockTestAnswer, FreeMockTestAnswerAdmin)


@admin.register(ChapterProgress)
class ChapterProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'chapter', 'completion_percentage')
    list_filter = ('chapter',)
