from django.urls import path
from . import views

urlpatterns = [
    path('question/', views.QuestionView.as_view(), name='theory'),
    path('lesson/', views.LessonView.as_view(), name='lesson'),
    path('chapter/', views.ChapterView.as_view(), name='chapter'),
    path('register/', views.RegisterView.as_view(), name='registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # path('study/', views.StudyChapterLessonDetails.as_view(), name='study'),
    path('chapters/', views.ChapterListView.as_view(), name="chapters"),
    path('lessons/', views.ChapterLessonsView.as_view(), name="lessons"),
    path('lessonDetails/<int:pk>', views.LessonDetailView.as_view(), name='lessonDetails'),
]
