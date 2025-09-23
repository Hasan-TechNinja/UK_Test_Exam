from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'subscription-plans', views.SubscriptionPlanViewSet)
router.register(r'user-subscriptions', views.UserSubscriptionViewSet, basename='user-subscription')

mock_test_viewset = views.MockTestViewSet.as_view({'post': 'start'})
free_mock_test = views.FreeMockTestViewSet.as_view({'get': 'retrieve',})


urlpatterns = [
    path('', include(router.urls)),

    # admin
    path('homeAdmin/', views.HomePageAdminView.as_view(), name='homeAdmin'),
    path('chapterAdmin/', views.ChapterAdminView.as_view(), name='chapterAdmin'),
    path('lessonAdmin/', views.LessonAdminView.as_view(), name='lessonAdmin'),
    path('lessonContentAdmin/', views.LessonContentAdminView.as_view(), name='lessonContents'),
    path('questionAdmin/', views.QuestionAdminView.as_view(), name='questionAdmin'),
    path('questionOptionsAdmin/', views.QuestionOptionAdminView.as_view(), name='questionOptionsAdmin'),
    path('guideAdmin/', views.GuideSupportAdminView.as_view(), name='guideAdmin'),
    path('guideContentAdmin/', views.GuideSupportContentAdminView.as_view(), name='guideContentAdmin'),
    path('subscriptionPlan/', views.SubscriptionPlanAdminView.as_view(), name = 'subscriptionPlan'),
    
    #admin details view
    path('homeAdmin/<int:pk>/', views.HomePageDetailsAdminView.as_view(), name='homeAdmin'),
    path('chapterAdmin/<int:pk>/', views.ChapterDetailsAdminView.as_view(), name='chapterAdmin'),
    path('lessonAdmin/<int:pk>/', views.LessonAdminDetailsView.as_view(), name='lessonAdmin'),
    path('lessonContentAdmin/<int:pk>/', views.LessonContentDetailsAdminView.as_view(), name='lessonContents'),
    path('questionAdmin/<int:pk>/', views.QuestionDetailsAdminView.as_view(), name='questionAdmin'),
    path('questionOptionsAdmin/<int:pk>/', views.QuestionOptionDetailsAdminView.as_view(), name='questionOptionsAdmin'),
    path('guideAdmin/<int:pk>/', views.GuideSupportDetailsAdminView.as_view(), name='guideAdmin'),
    path('guideContentAdmin/<int:pk>/', views.GuideSupportContentDetailsAdminView.as_view(), name='guideContentAdmin'),
    path('subscriptionPlan/<int:pk>/', views.SubscriptionPlanDetailsAdminView.as_view(), name = 'subscriptionPlan'),

    # authentication
    path('register/', views.RegisterView.as_view(), name='registration'),
    path('verify-email/', views.VerifyEmailView.as_view()),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('evaluation/', views.UserEvaluationView.as_view(), name='evaluation'),

    # user study
    path('home/', views.HomePageView.as_view(), name="home"),
    path('chapters/', views.ChapterListView.as_view(), name="chapters"),
    path('chapters/<int:pk>/', views.ChapterLessonsView.as_view(), name="chapters"),
    path('chapters/<int:chapter_id>/<int:lesson_id>/', views.ChapterLessonDetailView.as_view(), name="chapter-lesson-detail"),

    #Guide and support
    path('guide/', views.GuideSupportView.as_view(), name='guide'),
    path('guide/<int:guide_id>/', views.GuideSupportContentView.as_view(), name='guideDetails'),

    # practice question answer
    path('practice/chapters/', views.PracticeChapterList.as_view(), name='practice'),
    path('practice/chapters/<int:chapter_id>/question/', views.PracticeQuestionListView.as_view()),
    path('practice/answer/', views.SubmitAnswersView.as_view()),

    # mock test
    path('mock-test/summary/', views.MockTestHomeViewSet.as_view(), name='free-mock-test-summary'),
    # path('mock-tests/start/', views.MockTestViewSet.as_view({'post': 'start'})),
    # path('mock-tests/<int:pk>/', mock_test),
    # path('mock-tests/<int:pk>/answer/', views.MockTestViewSet.as_view({'post': 'answer'})),
    # path('mock-tests/<int:pk>/finish/', views.MockTestViewSet.as_view({'post': 'finish'})),
    # path('mock-tests/history/', views.MockTestViewSet.as_view({'get': 'history'})),

    # path('mock-test/start/', views.MockTestViewSet.as_view({'post': 'start'}), name='mock-test-start'),
    path('mock-test/start/', views.MockTestViewSet.as_view({'post': 'start','get': 'start',}), name='mock-test-start'),

    path('mock-test/<int:pk>/submit-all/', views.MockTestViewSet.as_view({'post': 'submit_all_answers'}), name='mock-test-submit-all'),
    path('mock-test/<int:pk>/', views.MockTestViewSet.as_view({'get': 'retrieve'}), name='mock-test-detail'),
    path('mock-test/<int:pk>/answer/', views.MockTestViewSet.as_view({'post': 'answer'}), name='mock-test-answer'),
    path('mock-test/<int:pk>/finish/', views.MockTestViewSet.as_view({'post': 'finish'}), name='mock-test-finish'),
    path('mock-test/history/', views.MockTestViewSet.as_view({'get': 'history'}), name='mock-test-history'),

    

    # free mock test
    # path('free-mock-tests/start/', views.FreeMockTestViewSet.as_view({'post': 'start'}), name='free-mock-start'),
    path('free-mock-tests/start/',views.FreeMockTestViewSet.as_view({'post': 'start','get': 'start',}), name='free-mock-start',),

    path('free-mock-tests/<int:pk>/', free_mock_test, name='free-mock-retrieve'),
    path('free-mock-tests/<int:pk>/answer/', views.FreeMockTestViewSet.as_view({'post': 'answer'}), name='free-mock-answer'),
    path('free-mock-tests/<int:pk>/finish/', views.FreeMockTestViewSet.as_view({'post': 'finish'}), name='free-mock-finish'),
    path('free-mock-tests/history/', views.FreeMockTestViewSet.as_view({'get': 'history'}), name='free-mock-history'),
    path('free-mock-tests/<int:pk>/submit-all-answers/',views.FreeMockTestViewSet.as_view({'post': 'submit_all_answers'}),name='free-mock-submit-all-answers'),

    # question upload
    path("upload-questions/", views.UploadCSVAPIView.as_view(), name="upload-questions"),

    path('student/', views.StudentView.as_view(), name='student'),
    path('chapters/count/', views.ChapterCountView.as_view(), name='chapter-count'),
    path('lessons/count/', views.LessonCountView.as_view(), name='lesson-count'),
    path('mock-tests/count/', views.MockTestCount.as_view(), name='mock-test-count'),
    path('subscription/count/', views.UserSubscriptionCount.as_view(), name='subscription-count'),

    path('upload-study-csv/', views.ImportLessonContentCSVView.as_view(), name='upload_csv'),
    path("upload-guidesupport-csv/", views.ImportGuideSupportCSVView.as_view(), name="upload_guidesupport_csv"),
    

]
    