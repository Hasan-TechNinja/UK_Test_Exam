from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser

# from main.models import LessonProgress
from .models import GuideChapter, GuideLesson, GuideLessonContent, GuideLessonProgress
from .serializers import ChapterModelSerializer, LessonModelSerializers, LessonContentModelSerializer
from django.db.models import Count, Q


# Create your views here.
class ChapterListView(APIView):
    permission_classes = [AllowAny]  # Allow both authenticated and unauthenticated users

    def get(self, request):
        chapters = GuideChapter.objects.all().order_by('id')
        data = []

        for chapter in chapters:
            lessons = GuideLesson.objects.filter(chapter=chapter).order_by('id')
            total_lessons = lessons.count()

            completed_lessons = 0
            lesson_ids = [str(lesson.name) for lesson in lessons]

            # Only calculate progress if the user is authenticated
            show_progress = request.user and not isinstance(request.user, AnonymousUser)

            if show_progress:
                for lesson in lessons:
                    progress = GuideLessonProgress.objects.filter(user=request.user, lesson=lesson).first()
                    if progress and progress.completion_percentage == 100.0:
                        completed_lessons += 1
                chapter_completion = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0.0
                completion_percentage = round(chapter_completion, 2)
            else:
                completion_percentage = None  # Or omit the field entirely if you prefer

            chapter_data = {
                'chapter_id': chapter.id,
                'name': chapter.name,
                'description': chapter.description,
                'created': chapter.created,
                'lessons': lesson_ids,
            }

            if show_progress:
                chapter_data['completion_percentage'] = completion_percentage

            data.append(chapter_data)

        return Response({
            "success": True,
            "message": "Chapters retrieved successfully.",
            "data": data
        }, status=status.HTTP_200_OK)


    
class ChapterLessonsView(APIView):
    permission_classes = [AllowAny]  # Allow all users to access

    def get(self, request, pk):
        chapter = get_object_or_404(GuideChapter, id=pk)
        lessons = GuideLesson.objects.filter(chapter=chapter).reverse()
        data = []

        show_progress = request.user and not isinstance(request.user, AnonymousUser)

        for lesson in lessons:
            lesson_data = {
                'lesson_id': lesson.id,
                'name': lesson.name,
                'title': lesson.title,
                'created': lesson.created,
            }

            if show_progress:
                progress = GuideLessonProgress.objects.filter(user=request.user, lesson=lesson).first()
                percentage = progress.completion_percentage if progress else 0.0
                lesson_data['completion_percentage'] = round(percentage, 2)

            data.append(lesson_data)

        return Response({
            "success": True,
            "message": "Lessons retrieved successfully.",
            "data": data
        }, status=status.HTTP_200_OK)




class ChapterLessonDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, chapter_id, lesson_id):
        lesson = get_object_or_404(GuideLesson, id=lesson_id, chapter_id=chapter_id)

        try:
            step = int(request.query_params.get('step', 0))
        except (TypeError, ValueError):
            return Response({
                "success": False,
                "message": "Invalid step value",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        PAGE_SIZE = 10
        start_index = step * PAGE_SIZE
        end_index = start_index + PAGE_SIZE

        lesson_qs = GuideLessonContent.objects.filter(lesson=lesson).order_by('id')
        total = lesson_qs.count()

        if start_index >= total:
            return Response({
                "success": False,
                "message": "No content available for this page.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        current_page_items = lesson_qs[start_index:end_index]

        completion_percentage = None  # Default for anonymous users

        if request.user.is_authenticated:
            user = request.user
            progress_obj, _ = GuideLessonProgress.objects.get_or_create(user=user, lesson=lesson)

            for content in current_page_items:
                if content not in progress_obj.completed_contents.all():
                    progress_obj.completed_contents.add(content)

            progress_obj.update_completion()
            completion_percentage = progress_obj.completion_percentage

        serializer = LessonContentModelSerializer(current_page_items, many=True)

        return Response({
            "success": True,
            "message": "Lesson content retrieved successfully.",
            "data": {
                "step": step,
                "total_items": total,
                "completion_percentage": completion_percentage,
                "content": serializer.data
            }
        }, status=status.HTTP_200_OK)


# update code 

# new comment 