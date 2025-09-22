from rest_framework import serializers
from .models import GuideChapter, GuideLesson, GuideLessonContent, GuideGlossary


class ChapterModelSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = GuideChapter
        fields = ['id', 'name', 'description', 'lessons']

    def get_lessons(self, obj):
        # lesson_qs = obj.guidelesson_set.all().order_by('id')
        lesson_qs = obj.lessons.all().order_by('id')

        # return [f"{i+1}" for i, _ in enumerate(lesson_qs)]
        return [{"id": l.id, "name": l.name, "title": l.title} for l in lesson_qs]



class LessonModelSerializers(serializers.ModelSerializer):
    # Read-only nested object for responses
    chapter = ChapterModelSerializer(read_only=True)
    # Write-only field for requests (accepts the id)
    chapter_id = serializers.PrimaryKeyRelatedField(
        source="chapter",
        queryset=GuideChapter.objects.all(),
        write_only=True
    )

    class Meta:
        model = GuideLesson
        # include both; created excluded as you had
        fields = ("id", "name", "title", "chapter", "chapter_id")


class GlossaryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideGlossary
        fields = ['id', 'title', 'description']


class LessonContentModelSerializer(serializers.ModelSerializer):
    chapter_name = serializers.CharField(source='lesson.chapter.name', read_only=True)
    glossaries = GlossaryModelSerializer(many=True, read_only=True)

    class Meta:
        model = GuideLessonContent
        fields = ['id', 'chapter_name', 'lesson', 'image', 'description', 'video', 'glossaries']