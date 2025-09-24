from django.contrib import admin
from .models import (
    GuideChapter,
    GuideLesson,
    GuideLessonContent,
    GuideGlossary,
    GuideLessonProgress,
)


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


@admin.register(GuideLessonContent)
class GuideLessonContentAdmin(admin.ModelAdmin):
    list_display = ("id", "lesson", "description", "video")
    search_fields = ("lesson__name", "lesson__title", "description")
    inlines = [GuideGlossaryInline]


# @admin.register(GuideGlossary)
# class GuideGlossaryAdmin(admin.ModelAdmin):
#     list_display = ("id", "title", "lesson_content", "description")
#     search_fields = ("title", "description", "lesson_content__lesson__name")


@admin.register(GuideLessonProgress)
class GuideLessonProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "lesson", "completion_percentage")
    list_filter = ("lesson", "user")
    search_fields = ("user__username", "lesson__name", "lesson__title")
    ordering = ("user", "lesson")

    # Make all fields read-only
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    # Disable add, change, and delete permissions
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
