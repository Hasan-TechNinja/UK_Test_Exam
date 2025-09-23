from django.urls import path
from . import views

urlpatterns = [
    path('chapters/', views.ChapterListView.as_view(), name="chapters"),
    path('chapters/<int:pk>/', views.ChapterLessonsView.as_view(), name="chapter-lessons"),
    path('chapters/<int:chapter_id>/<int:lesson_id>/', views.ChapterLessonDetailView.as_view(), name="chapter-lesson-detail"),


    path('chapterAdmin/', views.ChapterAdminView.as_view(), name='chapterAdmin'),
    path('lessonAdmin/', views.LessonAdminView.as_view(), name='lessonAdmin'),
    path('lessonContentAdmin/', views.LessonContentAdminView.as_view(), name='lessonContents'),

    path('chapterAdmin/<int:pk>/', views.ChapterDetailsAdminView.as_view(), name='chapterAdmin'),
    path('lessonAdmin/<int:pk>/', views.LessonAdminDetailsView.as_view(), name='lessonAdmin'),
    path('lessonContentAdmin/<int:pk>/', views.LessonContentDetailsAdminView.as_view(), name='lessonContents'),
]
