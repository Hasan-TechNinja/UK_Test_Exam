from django.contrib import admin, messages
from .models import (GuideChapter,GuideLesson,GuideLessonContent,GuideGlossary,GuideLessonProgress,)
import csv
from io import TextIOWrapper
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import path
from django.http import JsonResponse
from django import forms


class GuideGlossaryInline(admin.TabularInline):
    model = GuideGlossary
    extra = 1

class GuideLessonContentInline(admin.TabularInline):
    model = GuideLessonContent
    extra = 1


@admin.register(GuideChapter)
class GuideChapterAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "created")
    search_fields = ("name", "description")
    ordering = ("-created",)


@admin.register(GuideLesson)
class GuideLessonAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "title", "chapter", "created")
    list_filter = ("chapter",)
    search_fields = ("name", "title", "chapter__name")
    inlines = [GuideLessonContentInline]
    ordering = ("-created",)


class GuideLessonContentCSVUploadForm(forms.Form):
    guide_chapter = forms.ModelChoiceField(
        queryset=GuideChapter.objects.all(),
        required=False,
        label="Select Guide Chapter"
    )
    guide_lesson = forms.ModelChoiceField(
        queryset=GuideLesson.objects.all(),
        required=True,
        label="Select Guide Lesson"
    )
    csv_file = forms.FileField(label="CSV File for Lesson Content")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'guide_chapter' in self.data:
            try:
                chapter_id = int(self.data.get('guide_chapter'))
                self.fields['guide_lesson'].queryset = GuideLesson.objects.filter(chapter_id=chapter_id).order_by('name')
            except (ValueError, TypeError):
                pass


@admin.register(GuideLessonContent)
class GuideLessonContentAdmin(admin.ModelAdmin):
    list_display = ("id", "lesson", "description", "video")
    search_fields = ("lesson__name", "lesson__title", "description")
    inlines = [GuideGlossaryInline]

    change_list_template = "admin/guidelessoncontent_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='guidelessoncontent_upload_csv'),
            path('ajax/load-guide-lessons/', self.admin_site.admin_view(self.load_guide_lessons), name='guidelessoncontent_load_guide_lessons'),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            form = GuideLessonContentCSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                guide_chapter = form.cleaned_data['guide_chapter']
                guide_lesson = form.cleaned_data['guide_lesson']
                csv_file = form.cleaned_data['csv_file']

                if guide_lesson.chapter != guide_chapter:
                    self.message_user(request, "Selected lesson does not belong to the selected chapter.", level=messages.ERROR)
                    return render(request, "admin/upload_guidelessoncontent_csv.html", {'form': form, 'current_model': 'Guide Lesson Content'})

                try:
                    decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
                    reader = csv.reader(decoded_file)
                    header = next(reader)

                    try:
                        desc_idx = header.index("description")
                        video_idx = header.index("video")
                    except ValueError as e:
                        self.message_user(request, f"Missing required CSV column: {e}", level=messages.ERROR)
                        return render(request, "admin/upload_guidelessoncontent_csv.html", {'form': form, 'current_model': 'Guide Lesson Content'})

                    glossary_title_indices = [i for i, col in enumerate(header) if col == "glossary_title"]
                    glossary_description_indices = [i for i, col in enumerate(header) if col == "glossary_description"]

                    if len(glossary_title_indices) != len(glossary_description_indices):
                        self.message_user(request, "Mismatch in glossary_title and glossary_description columns in CSV.", level=messages.ERROR)
                        return render(request, "admin/upload_guidelessoncontent_csv.html", {'form': form, 'current_model': 'Guide Lesson Content'})

                    with transaction.atomic():
                        for row_data in reader:
                            description_val = row_data[desc_idx] if desc_idx < len(row_data) else ""
                            video_val = row_data[video_idx] if video_idx < len(row_data) else ""

                            guidel_content = GuideLessonContent.objects.create(
                                lesson=guide_lesson,
                                description=description_val,
                                video=video_val,
                            )

                            for i in range(len(glossary_title_indices)):
                                title_idx = glossary_title_indices[i]
                                desc_idx_glossary = glossary_description_indices[i]

                                glossary_title = row_data[title_idx] if title_idx < len(row_data) else ""
                                glossary_description = row_data[desc_idx_glossary] if desc_idx_glossary < len(row_data) else ""

                                if glossary_title:
                                    GuideGlossary.objects.create(
                                        lesson_content=guidel_content,
                                        title=glossary_title,
                                        description=glossary_description or ""
                                    )

                    self.message_user(request, "Guide Lesson Content CSV uploaded successfully!", level=messages.SUCCESS)
                    return redirect("admin:guide_guidelessoncontent_changelist")

                except Exception as e:
                    self.message_user(request, f"Error processing CSV: {str(e)}", level=messages.ERROR)
            else:
                self.message_user(request, "Please correct the errors in the form.", level=messages.ERROR)
        else:
            form = GuideLessonContentCSVUploadForm()

        return render(request, "admin/upload_guidelessoncontent_csv.html", {'form': form, 'current_model': 'Guide Lesson Content'})


    # AJAX endpoint to load GuideLessons based on selected GuideChapter
    def load_guide_lessons(self, request):
        chapter_id = request.GET.get('chapter_id')
        lessons = GuideLesson.objects.filter(chapter_id=chapter_id).order_by('name').values('id', 'name')
        return JsonResponse(list(lessons), safe=False)


@admin.register(GuideLessonProgress)
class GuideLessonProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "lesson", "completion_percentage")
    list_filter = ("lesson", "user")
    search_fields = ("user__username", "lesson__name", "lesson__title")
    ordering = ("user", "lesson")

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False