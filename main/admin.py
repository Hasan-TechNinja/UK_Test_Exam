from django.contrib import admin, messages
from . models import Chapter, Glossary, GuidesSupportGlossary, Lesson, Profile, GuidesSupport, GuideSupportContent, LessonContent, HomePage, QuestionGlossary, QuestionOption, Question, UserEvaluation, MockTestAnswer, MockTestSession, FreeMockTestSession, FreeMockTestAnswer, ChapterProgress, LessonProgress
from rest_framework.authtoken.models import Token
import csv
from io import TextIOWrapper
from django.db import transaction
from django.shortcuts import render, redirect
from .models import Chapter, Question, QuestionOption


# Register your models here.

class HomePageModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'description', 'image'
    )
admin.site.register(HomePage, HomePageModelAdmin)

class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name', 'description')
admin.site.register(Chapter, ChapterAdmin)

class GlossaryInline(admin.TabularInline):
    model = Glossary
    extra = 3


class LessonContentInline(admin.StackedInline):
    model = LessonContent
    extra = 1
    fieldsets = (
        (None, {
            'fields': ('image', 'description', 'video')
        }),
    )
    inlines = [GlossaryInline]  # Attach glossary inline inside LessonContent



class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'chapter')
    list_filter = ('chapter',)
    inlines = [LessonContentInline]



class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lesson', 'completion_percentage')

    # Make all fields read-only
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing existing object
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    # Disable add, change, and delete permissions
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(LessonProgress, LessonProgressAdmin)



class LessonContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'image', 'description', 'video')
    list_filter = ('lesson__chapter', 'lesson')
    search_fields = ('lesson__title', 'description')
    inlines = [GlossaryInline]


# class GlossaryAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'lesson_content', 'get_lesson', 'get_chapter')
#     list_filter = ('lesson_content__lesson__chapter', 'lesson_content__lesson')
#     search_fields = ('title', 'description')

#     def get_chapter(self, obj):
#         return obj.lesson_content.lesson.chapter.name
#     get_chapter.short_description = "Chapter"

#     def get_lesson(self, obj):
#         return obj.lesson_content.lesson.title
#     get_lesson.short_description = "Lesson"



admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonContent, LessonContentAdmin)
# admin.site.register(Glossary, GlossaryAdmin)



class ProfileModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'image', 'created_at')

    # Make all fields read-only
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing existing object
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    # Disable add, change, and delete permissions
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Profile, ProfileModelAdmin)



class UserEvaluationModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'MockTestTaken', 'LeftMockTest',
        'PracticeCompleted', 'QuestionAnswered',
        'CorrectAnswered', 'WrongAnswered'
    )

    # Make all fields read-only
    def get_readonly_fields(self, request, obj=None):
        if obj:  # when viewing an existing object
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    # Disable add, change, and delete
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(UserEvaluation, UserEvaluationModelAdmin)



# class GuidesSupportModelAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'title', 'created')


# admin.site.register(GuidesSupport, GuidesSupportModelAdmin)


# class GuidesSupportGlossaryInline(admin.TabularInline):
#     model = GuidesSupportGlossary
#     extra = 1



# class GuideSupportContentModelAdmin(admin.ModelAdmin):
#     list_display = ('id', 'guide', 'image', 'description', 'video', 'created')
#     inlines = [GuidesSupportGlossaryInline]


# admin.site.register(GuideSupportContent, GuideSupportContentModelAdmin)


# class MockTestSessionAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'user', 'started_at', 'finished_at', 'score', 'total_questions', 'duration_minutes', 
#     )
# admin.site.register(MockTestSession, MockTestSessionAdmin)



# class MockTestAnswerAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'session', 'question', 'is_correct'
#     )
# admin.site.register(MockTestAnswer, MockTestAnswerAdmin)



# class FreeMockTestSessionAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'user', 'started_at', 'finished_at', 'score', 'total_questions', 'duration_minutes', 
#     )
# admin.site.register(FreeMockTestSession, FreeMockTestSessionAdmin)



# class FreeMockTestAnswerAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'session', 'question', 'is_correct'
#     )
# admin.site.register(FreeMockTestAnswer, FreeMockTestAnswerAdmin)


@admin.register(ChapterProgress)
class ChapterProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'chapter', 'completion_percentage')
    list_filter = ('chapter',)

    # Make all fields read-only
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing existing object
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    # Disable add, change, and delete permissions
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False



class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 0


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'text', 'is_correct')
    list_filter = ('question', 'is_correct')
    search_fields = ('question__question_text', 'text')



# class QuestionGlossaryAdmin(admin.ModelAdmin):
#     list_display = ("id", "question", "title", "definition")

# admin.site.register(QuestionGlossary, QuestionGlossaryAdmin)



# Inline for Question Options
class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1

# Inline for Question Glossary
class QuestionGlossaryInline(admin.TabularInline):
    model = QuestionGlossary
    extra = 1

# Question Admin
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'chapter', 'type', 'question_text', 'explanation', 'image', 'multiple_answers')
    list_filter = ['type']
    search_fields = ['question_text', 'chapter__name']

    # Include both inlines
    inlines = [QuestionOptionInline, QuestionGlossaryInline]

    # Custom template for CSV upload
    change_list_template = "admin/questions_change_list.html"

    # Add custom URL for CSV upload
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='question_upload_csv'),
        ]
        return custom_urls + urls

    # CSV upload view
    def upload_csv(self, request):
        if request.method == "POST" and request.FILES.get("csv_file"):
            csv_file = request.FILES["csv_file"]

            try:
                decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
                reader = csv.DictReader(decoded_file)
                with transaction.atomic():
                    for row in reader:
                        chapter_id = row.get("chapter_id")
                        try:
                            chapter = Chapter.objects.get(id=chapter_id)
                        except Chapter.DoesNotExist:
                            self.message_user(
                                request, f"Chapter with id {chapter_id} not found.", level=messages.ERROR
                            )
                            continue

                        question = Question.objects.create(
                            chapter=chapter,
                            type=row.get("type", "practice"),
                            question_text=row.get("question_text"),
                            explanation=row.get("explanation", ""),
                            multiple_answers=row.get("multiple_answers", "false").lower() == "true"
                        )

                        # Create options dynamically (up to 9 options)
                        for i in range(1, 10):
                            option_text = row.get(f"option_{i}_text")
                            if option_text:
                                is_correct = row.get(f"option_{i}_correct", "false").lower() == "true"
                                QuestionOption.objects.create(
                                    question=question,
                                    text=option_text,
                                    is_correct=is_correct
                                )

                        # Create glossary entries dynamically (up to 9 glossaries)
                        for i in range(1, 10):
                            glossary_title = row.get(f"glossary_{i}_title")
                            glossary_definition = row.get(f"glossary_{i}_definition")
                            if glossary_title:
                                QuestionGlossary.objects.create(
                                    question=question,
                                    title=glossary_title,
                                    definition=glossary_definition or ""
                                )

                self.message_user(request, "CSV uploaded successfully!", level=messages.SUCCESS)
                return redirect("admin:main_question_changelist")

            except Exception as e:
                self.message_user(request, f"Error processing CSV: {str(e)}", level=messages.ERROR)

        return render(request, "admin/upload_csv.html")
