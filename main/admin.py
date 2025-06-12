from django.contrib import admin
from . models import Chapter, Lesson, Question, Profile, GuidesSupport, GuideSupportList, LessonContent, HomePage
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
        'id', 'lesson', 'image', 'description', 'video'
    )
admin.site.register(LessonContent, LessonContentModelAdmin)



class QuestionModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'description', 'option', 'image'
    )
admin.site.register(Question, QuestionModelAdmin)



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


class GuideSupportListModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'guide', 'image', 'video', 'created'
    )
admin.site.register(GuideSupportList, GuideSupportListModelAdmin)