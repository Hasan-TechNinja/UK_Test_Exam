from django.urls import path
from . import views

urlpatterns = [
    path('chapters/', views.ChapterListView.as_view(), name="chapters"),
    path('chapters/<int:pk>/', views.ChapterLessonsView.as_view(), name="chapter-lessons"),
    path('chapters/<int:chapter_id>/<int:lesson_id>/', views.ChapterLessonDetailView.as_view(), name="chapter-lesson-detail"),
]
