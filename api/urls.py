from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'subscription-plans', views.SubscriptionPlanViewSet)
router.register(r'user-subscriptions', views.UserSubscriptionViewSet, basename='user-subscription')


urlpatterns = [
    path('', include(router.urls)),

    # admin
    path('homeAdmin/', views.HomePageAdminView.as_view(), name='homeAdmin'),
    path('chapterAdmin/', views.ChapterAdminView.as_view(), name='chapterAdmin'),
    path('lessonAdmin/', views.LessonAdminView.as_view(), name='lessonAdmin'),
    path('questionAdmin/', views.QuestionAdminView.as_view(), name='theoryAdmin'),
    path('PracticeQuestionAdmin/', views.PracticeQuestionOptionAdminView.as_view(), name='PracticeQuestionAdmin'),
    path('guideAdmin/', views.GuideSupportAdminView.as_view(), name='guideAdmin'),
    path('subscriptionPlan/', views.SubscriptionPlanAdminView.as_view(), name = 'subscriptionPlan'),
    
    #admin details view
    path('homeAdmin/<int:pk>', views.HomePageDetailsAdminView.as_view(), name='homeAdmin'),
    path('chapterAdmin/<int:pk>', views.ChapterDetailsAdminView.as_view(), name='chapterAdmin'),
    path('lessonAdmin/<int:pk>', views.LessonContentDetailsAdminView.as_view(), name='lessonAdmin'),
    path('questionAdmin/<int:pk>', views.QuestionDetailsAdminView.as_view(), name='questionAdmin'),
    path('PracticeQuestionAdmin/<int:pk>', views.PracticeQuestionOptionDetailsAdminView.as_view(), name='PracticeQuestionAdmin'),
    path('guideAdmin/<int:pk>', views.GuideSupportDetailsAdminView.as_view(), name='guideAdmin'),
    path('guideAdmin/<int:pk>', views.GuideSupportContentDetailsAdminView.as_view(), name='guideAdmin'),
    path('subscriptionPlan/<int:pk>', views.SubscriptionPlanDetailsAdminView.as_view(), name = 'subscriptionPlan'),

    # authentication
    path('register/', views.RegisterView.as_view(), name='registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # user 
    path('home/', views.HomePageView.as_view(), name="home"),
    path('chapters/', views.ChapterListView.as_view(), name="chapters"),
    path('chapters/<int:pk>', views.ChapterLessonsView.as_view(), name="chapters"),
    path('chapters/<int:chapter_id>/<int:lesson_id>/', views.ChapterLessonDetailView.as_view(), name="chapter-lesson-detail"),
    path('guide/', views.GuideSupportView.as_view(), name='guid'),
    path('guide/<int:guide_id>/', views.GuideSupportContentView.as_view(), name='guideDetails'),


    # practice question answer
    # path('practice/chapters/', views.PracticeChapterList.as_view(), name='practice-chapters'),
    # path('practice/chapters/<int:chapter_id>/questions/', views.ChapterQuestionList.as_view(), name='chapter-questions'),
    # path('practice/submit/', views.SubmitAnswers.as_view(), name='submit-practice-answers'),
    path('practice/chapters/<int:chapter_id>/question/', views.QuestionStepView.as_view()),
    path('practice/answer/', views.SubmitAnswerView.as_view()),

]
