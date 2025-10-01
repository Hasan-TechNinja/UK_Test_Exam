from django.contrib import admin, messages
from . models import Chapter, Glossary, GuidesSupportGlossary, Lesson, Profile, GuidesSupport, GuideSupportContent, LessonContent, HomePage, QuestionGlossary, QuestionOption, Question, UserEvaluation, MockTestAnswer, MockTestSession, FreeMockTestSession, FreeMockTestAnswer, ChapterProgress, LessonProgress
from rest_framework.authtoken.models import Token
import csv
from io import TextIOWrapper
from django.db import transaction
from django.shortcuts import render, redirect
from .models import Chapter, Question, QuestionOption

from django import forms
from django.http import JsonResponse
from django.urls import path


# Register your models here.

class HomePageModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'description', 'image'
    )
admin.site.register(HomePage, HomePageModelAdmin)

# class ChapterAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'description')
#     search_fields = ('name', 'description')
# admin.site.register(Chapter, ChapterAdmin)

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



# class LessonAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'chapter')
#     list_filter = ('chapter',)
#     inlines = [LessonContentInline]



class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lesson', 'completion_percentage')

    # Make all fields read-only
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing existing object
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    # Disable add, change, and delete permissions
    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


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



# admin.site.register(Lesson, LessonAdmin)
# admin.site.register(LessonContent, LessonContentAdmin)
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
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


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
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


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
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True



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



# ---------- Inlines ----------
class GlossaryInline(admin.TabularInline):
    model = Glossary
    extra = 1


class LessonContentInline(admin.TabularInline):
    model = LessonContent
    extra = 1


# ---------- Chapter ----------
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "created")
    search_fields = ("name", "description")
    ordering = ("-created",)


# ---------- Lesson ----------
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "title", "chapter", "created")
    list_filter = ("chapter",)
    search_fields = ("name", "title", "chapter__name")
    inlines = [LessonContentInline]
    ordering = ("-created",)


# ---------- CSV Upload Form ----------
class LessonContentCSVUploadForm(forms.Form):
    chapter = forms.ModelChoiceField(
        queryset=Chapter.objects.all(),
        required=False,
        label="Select Chapter"
    )
    lesson = forms.ModelChoiceField(
        queryset=Lesson.objects.all(),
        required=True,
        label="Select Lesson"
    )
    csv_file = forms.FileField(label="CSV File for Lesson Content")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "chapter" in self.data:
            try:
                chapter_id = int(self.data.get("chapter"))
                self.fields["lesson"].queryset = Lesson.objects.filter(
                    chapter_id=chapter_id
                ).order_by("name")
            except (ValueError, TypeError):
                pass


# ---------- Lesson Content ----------
@admin.register(LessonContent)
class LessonContentAdmin(admin.ModelAdmin):
    list_display = ("id", "lesson", "description", "video")
    search_fields = ("lesson__name", "lesson__title", "description")
    inlines = [GlossaryInline]

    change_list_template = "admin/lessoncontent_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload-csv/",
                self.admin_site.admin_view(self.upload_csv),
                name="lessoncontent_upload_csv",
            ),
            path(
                "ajax/load-lessons/",
                self.admin_site.admin_view(self.load_lessons),
                name="lessoncontent_load_lessons",
            ),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            form = LessonContentCSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                chapter = form.cleaned_data["chapter"]
                lesson = form.cleaned_data["lesson"]
                csv_file = form.cleaned_data["csv_file"]

                if chapter and lesson.chapter != chapter:
                    self.message_user(
                        request,
                        "Selected lesson does not belong to the selected chapter.",
                        level=messages.ERROR,
                    )
                    return render(
                        request,
                        "admin/upload_lessoncontent_csv.html",
                        {"form": form, "current_model": "Lesson Content"},
                    )

                try:
                    decoded_file = TextIOWrapper(csv_file.file, encoding="utf-8")
                    reader = csv.reader(decoded_file)
                    header = next(reader)

                    try:
                        desc_idx = header.index("description")
                        video_idx = header.index("video")
                    except ValueError as e:
                        self.message_user(
                            request,
                            f"Missing required CSV column: {e}",
                            level=messages.ERROR,
                        )
                        return render(
                            request,
                            "admin/upload_lessoncontent_csv.html",
                            {"form": form, "current_model": "Lesson Content"},
                        )

                    glossary_title_indices = [
                        i for i, col in enumerate(header) if col == "glossary_title"
                    ]
                    glossary_desc_indices = [
                        i for i, col in enumerate(header) if col == "glossary_description"
                    ]

                    if len(glossary_title_indices) != len(glossary_desc_indices):
                        self.message_user(
                            request,
                            "Mismatch in glossary_title and glossary_description columns in CSV.",
                            level=messages.ERROR,
                        )
                        return render(
                            request,
                            "admin/upload_lessoncontent_csv.html",
                            {"form": form, "current_model": "Lesson Content"},
                        )

                    with transaction.atomic():
                        for row_data in reader:
                            description_val = row_data[desc_idx] if desc_idx < len(row_data) else ""
                            video_val = row_data[video_idx] if video_idx < len(row_data) else ""

                            lesson_content = LessonContent.objects.create(
                                lesson=lesson,
                                description=description_val,
                                video=video_val,
                            )

                            for i in range(len(glossary_title_indices)):
                                t_idx = glossary_title_indices[i]
                                d_idx = glossary_desc_indices[i]

                                glossary_title = row_data[t_idx] if t_idx < len(row_data) else ""
                                glossary_description = row_data[d_idx] if d_idx < len(row_data) else ""

                                if glossary_title:
                                    Glossary.objects.create(
                                        lesson_content=lesson_content,
                                        title=glossary_title,
                                        description=glossary_description or "",
                                    )

                    self.message_user(
                        request,
                        "Lesson Content CSV uploaded successfully!",
                        level=messages.SUCCESS,
                    )
                    # ✅ auto-generate the correct admin changelist URL
                    return redirect(
                        "admin:%s_%s_changelist"
                        % (LessonContent._meta.app_label, LessonContent._meta.model_name)
                    )

                except Exception as e:
                    self.message_user(
                        request, f"Error processing CSV: {str(e)}", level=messages.ERROR
                    )
            else:
                self.message_user(
                    request, "Please correct the errors in the form.", level=messages.ERROR
                )
        else:
            form = LessonContentCSVUploadForm()

        return render(
            request,
            "admin/upload_lessoncontent_csv.html",
            {"form": form, "current_model": "Lesson Content"},
        )


    # AJAX endpoint to load Lessons based on Chapter
    def load_lessons(self, request):
        chapter_id = request.GET.get("chapter_id")
        lessons = Lesson.objects.filter(chapter_id=chapter_id).order_by("name").values(
            "id", "name"
        )
        return JsonResponse(list(lessons), safe=False)
