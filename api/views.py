from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import authenticate
from datetime import timedelta
import random
from django.db.models import Max
from django.contrib.auth.models import AnonymousUser

from main.models import Lesson, Chapter, Profile, GuidesSupport, HomePage, GuideSupportContent, LessonContent, UserEvaluation, Question, QuestionOption, MockTestSession, MockTestAnswer, FreeMockTestSession, FreeMockTestAnswer, ChapterProgress, LessonProgress
from subscriptions.models import SubscriptionPlan, UserSubscription
from . serializers import LessonModelSerializers, ChapterModelSerializer, RegisterSerializer, ProfileModelSerializer, GuidesSupportModelSerializer, HomePageModelSerializer, GuideSupportContentModelSerializer, LessonContentModelSerializer, UserEvaluationModelSerializer, SubscriptionPlanSerializer, UserSubscriptionSerializer, QuestionOptionSerializer, QuestionSerializer, StartMockTestSerializer, MockTestAnswerSerializer, MockTestResultSerializer, FreeMockTestAnswerSerializer, FreeMockTestResultSerializer, FreeStartMockTestSerializer

from rest_framework.views import View, APIView
from rest_framework import mixins, generics, status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
import csv
from io import TextIOWrapper
from django.contrib.auth import get_user_model
from main.models import EmailVerification, PasswordResetCode
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password

#  Create your views here.


# -----------------------------------------------Authentication section----------------------------------
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "message": "User registered successfully. Please verify your email.",
                "data": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Registration failed.",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



User = get_user_model()

class VerifyEmailView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        try:
            user = User.objects.get(email=email)
            verification = EmailVerification.objects.get(user=user)

            if verification.code != code:
                return Response({
                    "success": False,
                    "message": "Invalid verification code.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            if verification.is_expired():
                user.delete()
                return Response({
                    "success": False,
                    "message": "Verification code expired. User has been deleted.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.save()
            verification.delete()

            return Response({
                "success": True,
                "message": "Email verified successfully. User is now active.",
                "data": {
                    "email": user.email
                }
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "User not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        except EmailVerification.DoesNotExist:
            return Response({
                "success": False,
                "message": "Verification record not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({
                "success": False,
                "message": "Email is required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "User with this email does not exist.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        # Generate and store code
        code = str(random.randint(100000, 999999))
        PasswordResetCode.objects.update_or_create(user=user, defaults={"code": code})

        # Send the code via email
        send_mail(
            'Your Password Reset Code',
            f'Your password reset code is: {code}',
            'noreply@example.com',
            [email],
            fail_silently=False
        )

        return Response({
            "success": True,
            "message": "Password reset code sent to email.",
            "data": None
        }, status=status.HTTP_200_OK)



class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        new_password = request.data.get("new_password")

        if not email or not code or not new_password:
            return Response({
                "success": False,
                "message": "Email, code, and new password are required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            reset = PasswordResetCode.objects.get(user=user)

            if reset.code != code:
                return Response({
                    "success": False,
                    "message": "Invalid reset code.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            if reset.is_expired():
                reset.delete()
                return Response({
                    "success": False,
                    "message": "Reset code expired.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate password
            validate_password(new_password, user=user)

            user.set_password(new_password)
            user.save()

            reset.delete()

            return Response({
                "success": True,
                "message": "Password reset successful.",
                "data": None
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "User not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except PasswordResetCode.DoesNotExist:
            return Response({
                "success": False,
                "message": "Reset code not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)



User = get_user_model()

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "Invalid email or password",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({
                "success": False,
                "message": "Invalid email or password",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                "success": False,
                "message": "User account is inactive",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)

        return Response({
            "success": True,
            "message": "Login successful",
            "data": {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
        }, status=status.HTTP_200_OK)

    

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if refresh_token is None:
            return Response({
                "success": False,
                "message": "Refresh token is required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                "success": True,
                "message": "Logout successful.",
                "data": None
            }, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({
                "success": False,
                "message": "Invalid or expired refresh token.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileModelSerializer

    def get_object(self):
        return self.request.user.profile

    def get(self, request, *args, **kwargs):
        try:
            profile = self.get_object()
            serializer = self.get_serializer(profile)
            return Response({
                "success": True,
                "message": "Profile retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            profile = self.get_object()
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Profile updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "message": "Invalid data provided.",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

class UserEvaluationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            evaluation = UserEvaluation.objects.get(user=request.user.profile)
        except UserEvaluation.DoesNotExist:
            return Response({
                "success": False,
                "message": "Evaluation not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            total = int(evaluation.QuestionAnswered or 0)
            correct = int(evaluation.CorrectAnswered or 0)
            wrong = int(evaluation.WrongAnswered or 0)
        except ValueError:
            total = correct = wrong = 0

        if total > 0:
            correct_percentage = round((correct / total) * 100, 2)
            wrong_percentage = round((wrong / total) * 100, 2)
        else:
            correct_percentage = wrong_percentage = 0.0

        user = request.user
        chapter_progress_qs = ChapterProgress.objects.filter(user=user).select_related("chapter")

        valid_progress = [
            p for p in chapter_progress_qs
            if p.chapter.questions.filter(type="practice").exists()
        ]

        if valid_progress:
            total_percent = sum(p.completion_percentage for p in valid_progress)
            overall_practice_completion = round(total_percent / len(valid_progress), 2)
        else:
            overall_practice_completion = 0.0

        response_data = {
            "MockTestTaken": evaluation.MockTestTaken,
            "LeftMockTest": evaluation.LeftMockTest,
            "PracticeCompleted": overall_practice_completion,
            "QuestionAnswered": total,
            "CorrectAnsweredPercentage": correct_percentage,
            "WrongAnsweredPercentage": wrong_percentage,
        }

        return Response({
            "success": True,
            "message": "User evaluation data retrieved successfully.",
            "data": response_data
        }, status=status.HTTP_200_OK)


        
# --------------------------------------------------Admin Control---------------------------------------------

class HomePageAdminView(generics.ListCreateAPIView):
    queryset = HomePage.objects.all()
    serializer_class = HomePageModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class QuestionAdminView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class QuestionOptionAdminView(generics.ListCreateAPIView):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class LessonAdminView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonModelSerializers
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    
    
class LessonContentAdminView(generics.ListCreateAPIView):
    queryset = LessonContent.objects.all()
    serializer_class = LessonContentModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class ChapterAdminView(generics.ListCreateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class GuideSupportAdminView(generics.ListCreateAPIView):
    queryset = GuidesSupport.objects.all()
    serializer_class = GuidesSupportModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class GuideSupportContentAdminView(generics.ListCreateAPIView):
    queryset = GuideSupportContent.objects.all()
    serializer_class = GuideSupportContentModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class SubscriptionPlanAdminView(generics.ListCreateAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


# --------------------------------------------------Admin details view--------------------------------------s

class HomePageDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HomePage.objects.all()
    serializer_class = HomePageModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

class ChapterDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"


class LessonAdminDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonModelSerializers
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

class LessonDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonModelSerializers
    permission_classes = [IsAdminUser]
    lookup_field = "pk"


class LessonContentDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LessonContent
    serializer_class = LessonContentModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"


class QuestionDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

class QuestionOptionDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"


class GuideSupportDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GuidesSupport.objects.all()
    serializer_class = GuidesSupportModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

class GuideSupportContentDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GuidesSupport.objects.all()
    serializer_class = GuidesSupportModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

class SubscriptionPlanDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

# --------------------------------------------------------Study section--------------------------------------

class HomePageView(APIView):
    def get(self, request):
        home = HomePage.objects.last()
        if home:
            serializer = HomePageModelSerializer(home)
            return Response({
                "success": True,
                "message": "Home page content retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "No home page content found.",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)



class ChapterListView(APIView):
    permission_classes = [AllowAny]  # Allow both authenticated and unauthenticated users

    def get(self, request):
        chapters = Chapter.objects.all().order_by('id')
        data = []

        for chapter in chapters:
            lessons = Lesson.objects.filter(chapter=chapter).order_by('id')
            total_lessons = lessons.count()

            completed_lessons = 0
            lesson_ids = [str(lesson.name) for lesson in lessons]

            # Only calculate progress if the user is authenticated
            show_progress = request.user and not isinstance(request.user, AnonymousUser)

            if show_progress:
                for lesson in lessons:
                    progress = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
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
        chapter = get_object_or_404(Chapter, id=pk)
        lessons = Lesson.objects.filter(chapter=chapter).reverse()
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
                progress = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
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
        lesson = get_object_or_404(Lesson, id=lesson_id, chapter_id=chapter_id)

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

        lesson_qs = LessonContent.objects.filter(lesson=lesson).order_by('id')
        total = lesson_qs.count()

        if start_index >= total:
            return Response({
                "success": False,
                "message": "No content available for this page.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        current_page_items = lesson_qs[start_index:end_index]

        completion_percentage = None  # Default for anonymous users

        # Update progress only if user is authenticated
        if request.user.is_authenticated:
            user = request.user
            progress_obj, _ = LessonProgress.objects.get_or_create(user=user, lesson=lesson)

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



    
# -----------------------------------------------------Guides & Support section-------------------------------------
    
class GuideSupportView(APIView):
    """
    GET /guides/
    """
    def get(self, request):
        guides = GuidesSupport.objects.all().order_by('id')
        serializer = GuidesSupportModelSerializer(guides, many=True)
        
        return Response({
            "success": True,
            "message": "Guides retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class GuideSupportContentView(APIView):
    """
    GET /guide/<guide_id>/?step=0
    Returns 10 items per step (pagination)
    """
    PAGE_SIZE = 10

    def get(self, request, guide_id):
        try:
            step = int(request.query_params.get("step", 0))
        except (TypeError, ValueError):
            return Response({
                "success": False,
                "message": "Step must be an integer.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        guide = get_object_or_404(GuidesSupport, pk=guide_id)
        title = guide.title

        contents_qs = GuideSupportContent.objects.filter(
            guide_id=guide_id
        ).order_by("id")

        total = contents_qs.count()
        start = step * self.PAGE_SIZE
        end = start + self.PAGE_SIZE

        if start >= total:
            return Response({
                "success": False,
                "message": "No content available for this page.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        current_items = contents_qs[start:end]

        # Serialize manually with glossary_list
        content_data = []
        for item in current_items:
            content_data.append({
                "id": item.id,
                "image": request.build_absolute_uri(item.image.url) if item.image else None,
                "description": item.description,
                "video": item.video,
                "created": item.created,
                "glossary_list": item.get_glossary_string_list(),
            })

        return Response({
            "success": True,
            "message": "Guide content retrieved successfully.",
            "data": {
                "title": title,
                "step": step,
                "total_items": total,
                "content": content_data
            }
        }, status=status.HTTP_200_OK)




# -----------------------------------Subscription----------------


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows subscription plans to be viewed.
    Accessible to anyone.
    """
    queryset = SubscriptionPlan.objects.all().order_by('price')
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]  # Anyone can see the available plans

    def list(self, request, *args, **kwargs):
        """
        Overriding the default list method to match the response structure.
        """
        response_data = super().list(request, *args, **kwargs)
        return Response({
            "success": True,
            "message": "Subscription plans retrieved successfully.",
            "data": response_data.data
        }, status=status.HTTP_200_OK)


class UserSubscriptionViewSet(viewsets.GenericViewSet):
    """
    API endpoint for managing user subscriptions.
    Requires authentication.
    """
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Ensure users can only see/manage their own subscriptions.
        """
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Retrieves the current user's subscription status.
        """
        try:
            user_subscription = self.get_queryset().get()  # Should be OneToOne, so get() works
            serializer = self.get_serializer(user_subscription)
            return Response({
                "success": True,
                "message": "User subscription retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except UserSubscription.DoesNotExist:
            return Response({
                "success": False,
                "message": "No active subscription found for this user.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        """
        Allows a user to subscribe to a specific plan.
        This endpoint would typically integrate with a payment gateway.
        For this tutorial, we'll simulate a successful payment.
        """
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({
                "success": False,
                "message": "Plan ID is required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({
                "success": False,
                "message": "Subscription plan not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():  # Ensure atomicity of database operations
            user = request.user
            user_subscription, created = UserSubscription.objects.get_or_create(user=user)

            # Update subscription details
            user_subscription.plan = plan
            user_subscription.is_active = True
            user_subscription.start_date = timezone.now()
            user_subscription.last_renewed = timezone.now()

            if plan.duration_days:
                user_subscription.end_date = user_subscription.start_date + timedelta(days=plan.duration_days)
            else:
                user_subscription.end_date = None

            user_subscription.save()

            if plan.duration_days is None:
                try:
                    profile = request.user.profile
                    evaluation = UserEvaluation.objects.get(user=profile)
                except UserEvaluation.DoesNotExist:
                    evaluation = UserEvaluation.objects.create(
                        user=profile,
                        PracticeCompleted='0',
                        QuestionAnswered='0',
                        CorrectAnswered='0',
                        WrongAnswered='0'
                    )

                evaluation.LeftMockTest = 'Unlimited'
                evaluation.save()

            serializer = self.get_serializer(user_subscription)
            return Response({
                "success": True,
                "message": "Subscription updated successfully." if not created else "Subscription created successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def cancel(self, request):
        """
        Allows a user to cancel their active subscription.
        Does not refund, just deactivates the subscription.
        """
        try:
            user_subscription = self.get_queryset().get()
            if not user_subscription.is_active:
                return Response({
                    "success": False,
                    "message": "Subscription is already inactive.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            user_subscription.is_active = False
            user_subscription.save()
            serializer = self.get_serializer(user_subscription)
            return Response({
                "success": True,
                "message": "Subscription canceled successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except UserSubscription.DoesNotExist:
            return Response({
                "success": False,
                "message": "No active subscription found to cancel.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)




#-------------------------------------Practice Chapter view-------------------------------------

class PracticeChapterList(APIView):
    permission_classes = [AllowAny]  # Allow both authenticated and unauthenticated users

    def get(self, request):
        user = request.user
        is_authenticated = user and not isinstance(user, AnonymousUser)

        chapters = Chapter.objects.all()
        data = []

        for chapter in chapters:
            total_questions = Question.objects.filter(chapter=chapter, type="practice").count()

            chapter_data = {
                'id': chapter.id,
                'name': chapter.name,
                'description': chapter.description,
                'total_questions': total_questions,
            }

            if is_authenticated:
                try:
                    progress = ChapterProgress.objects.get(user=user, chapter=chapter)
                    completion_percentage = round(progress.completion_percentage, 2)
                except ChapterProgress.DoesNotExist:
                    completion_percentage = 0.0

                chapter_data['completion_percentage'] = completion_percentage

            data.append(chapter_data)

        return Response({
            "success": True,
            "message": "Chapters retrieved successfully.",
            "data": data
        }, status=status.HTTP_200_OK)



'''
PAGE_SIZE = 1

class PracticeQuestionStepView(APIView):
    """
    GET /practice/chapters/<chapter_id>/question/?step=0
    Returns exactly one question (index = step)
    """
    def get(self, request, chapter_id):
        try:
            step = int(request.query_params.get("step", 0))
        except (TypeError, ValueError):
            return Response({"detail": "step must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        qs     = Question.objects.filter(type = "practice", chapter_id=chapter_id).order_by("id")
        total  = qs.count()

        if step < 0 or step >= total:
            return Response({"detail": "Invalid step index."},
                            status=status.HTTP_404_NOT_FOUND)

        question = qs[step]
        data     = QuestionSerializer(question).data
        return Response({
            "step":   step,
            "total":  total,
            "has_prev": step > 0,
            "has_next": step < total - 1,
            "question": data
        })
'''

class PracticeQuestionListView(APIView):
    """
    GET /practice/chapters/<chapter_id>/questions/
    Returns all practice questions in a chapter with options
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, chapter_id):
        questions = Question.objects.filter(type="practice", chapter_id=chapter_id).order_by("id")
        serialized = QuestionSerializer(questions, many=True).data
        return Response({
            "success": True,
            "message": "Practice questions retrieved successfully.",
            "data": {
                "total": questions.count(),
                "questions": serialized
            }
        }, status=status.HTTP_200_OK)

'''
class SubmitAnswerView(APIView):
    """
    POST /practice/answer/
    {
        "chapter_id": 1,
        "step": 0,
        "question_id": 15,
        "selected_options": [42]
    }
    Returns next question OR final result if finished.
    """
    def post(self, request):
        chapter_id       = request.data.get("chapter_id")
        step             = int(request.data.get("step", 0))
        question_id      = request.data.get("question_id")
        selected_options = set(request.data.get("selected_options", []))

        # Validate question
        try:
            question = Question.objects.get(type = "practice", id=question_id, chapter_id=chapter_id)
        except Question.DoesNotExist:
            return Response({"detail": "Invalid question."}, status=status.HTTP_400_BAD_REQUEST)

        correct_set = set(question.options.filter(is_correct=True).values_list('id', flat=True))
        is_correct  = selected_options == correct_set

        # ----- you can persist attempt here if you wish -----
        user = request.user
        progress_obj, _ = ChapterProgress.objects.get_or_create(user=user, chapter_id=chapter_id)

        # Mark this question as completed if not already
        if question not in progress_obj.completed_questions.all():
            progress_obj.completed_questions.add(question)
            progress_obj.update_completion()

        # Prepare result for this question
        question_result = {
            "question_id": question_id,
            "is_correct":  is_correct,
            "correct_options": list(correct_set),
            "selected_options": list(selected_options),
            "explanation": question.explanation,
        }

        # Determine next step
        qs    = Question.objects.filter(type = "practice", chapter_id=chapter_id).order_by("id")
        total = qs.count()
        next_step = step + 1

        if next_step >= total:
            # last question answered – return summary
            # NOTE: Ideally accumulate answers in session/db to compute score.
            # For demo, we send only current result and flag completion.
            return Response({
                "completed": True,
                "question_result": question_result,
            }, status=status.HTTP_200_OK)

        # Otherwise send the next question
        next_q   = qs[next_step]
        next_ser = QuestionSerializer(next_q)

        return Response({
            "completed": False,
            "question_result": question_result,
            "completion_percentage": progress_obj.completion_percentage,
            "next_question": {
                "step": next_step,
                "total": total,
                "question": next_ser.data,
                "has_next": next_step < total - 1,
                "has_prev": True
            }
        }, status=status.HTTP_200_OK)
'''

class SubmitAnswersView(APIView):
    """
    POST /practice/submit-answers/
    {
        "chapter_id": 1,
        "answers": [
            {
                "question_id": 15,
                "selected_options": [42, 43]
            },
            ...
        ]
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        chapter_id = request.data.get("chapter_id")
        answers = request.data.get("answers", [])

        if not answers:
            return Response({
                "success": False,
                "message": "Answers list is required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        progress_obj, _ = ChapterProgress.objects.get_or_create(user=user, chapter_id=chapter_id)

        results = []
        correct_count = 0

        for ans in answers:
            question_id = ans.get("question_id")
            selected = set(ans.get("selected_options", []))

            try:
                question = Question.objects.get(id=question_id, type="practice", chapter_id=chapter_id)
            except Question.DoesNotExist:
                continue  # skip invalid question

            correct_set = set(question.options.filter(is_correct=True).values_list('id', flat=True))
            is_correct = selected == correct_set

            if question not in progress_obj.completed_questions.all():
                progress_obj.completed_questions.add(question)

            results.append({
                "question_id": question_id,
                "is_correct": is_correct,
                "correct_options": list(correct_set),
                "selected_options": list(selected),
                "explanation": question.explanation,
            })

            if is_correct:
                correct_count += 1

        progress_obj.update_completion()

        return Response({
            "success": True,
            "message": "Answers submitted successfully.",
            "data": {
                "completed": True,
                "total_questions": len(answers),
                "correct_answers": correct_count,
                "completion_percentage": progress_obj.completion_percentage,
                "results": results
            }
        }, status=status.HTTP_200_OK)



# ______________-----------------------------------Mock Test--------------------------------______________


class MockTestHomeViewSet(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        is_logged_in = user.is_authenticated

        if is_logged_in:
            latest_session = MockTestSession.objects.filter(user=user).order_by('-started_at').first()
        else:
            latest_session = None

        total_questions = latest_session.total_questions if latest_session else 24
        duration_minutes = latest_session.duration_minutes if latest_session else 45

        response_data = {
            "mock_test_config": {
                "total_questions": total_questions,
                "duration_minutes": duration_minutes
            }
        }

        if is_logged_in:
            total_tests = MockTestSession.objects.filter(user=user, finished_at__isnull=False).count()
            best_score = MockTestSession.objects.filter(
                user=user, finished_at__isnull=False, score__isnull=False
            ).aggregate(Max('score'))['score__max'] or 0

            response_data["view_past_tests"] = {
                "total_tests_taken": total_tests,
                "best_score": f"{best_score}%"
            }

        return Response({
            "success": True,
            "message": "Mock test configuration retrieved successfully.",
            "data": response_data
        }, status=status.HTTP_200_OK)




'''
class MockTestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def start(self, request):
        total_questions = 24
        questions = list(Question.objects.filter(type = "mockTest"))

        if len(questions) < total_questions:
            return Response({'error': 'Not enough questions to start the test.'}, status=status.HTTP_400_BAD_REQUEST)

        selected_questions = random.sample(questions, total_questions)
        session = MockTestSession.objects.create(user=request.user, total_questions=total_questions)

        for q in selected_questions:
            MockTestAnswer.objects.create(session=session, question=q)

        # Update UserEvaluation
        profile = request.user.profile
        evaluation, _ = UserEvaluation.objects.get_or_create(user=profile)
        evaluation.MockTestTaken += 1
        evaluation.save(update_fields=['MockTestTaken'])

        return Response(StartMockTestSerializer(session).data)

    def retrieve(self, request, pk=None):
        session = get_object_or_404(MockTestSession, pk=pk, user=request.user)
        answers = session.answers.select_related('question').prefetch_related('selected_choices', 'question__options')
        data = []
        for a in answers:
            data.append({
                'question': QuestionSerializer(a.question).data,
                'selected_choices': list(a.selected_choices.values_list('id', flat=True)),
                'is_correct': a.is_correct
            })
        return Response({'session_id': session.id, 'answers': data})

    @action(detail=True, methods=['post'])
    def answer(self, request, pk=None):
        session = get_object_or_404(MockTestSession, pk=pk, user=request.user)
        question_id = request.data.get('question')
        choice_ids = request.data.get('selected_choice_ids', [])

        if question_id is None or not isinstance(choice_ids, list):
            return Response({'error': 'Both "question" and "selected_choice_ids" are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            answer = MockTestAnswer.objects.get(session=session, question_id=question_id)
        except MockTestAnswer.DoesNotExist:
            return Response({'error': 'Question not found in this session.'}, status=status.HTTP_400_BAD_REQUEST)

        valid_choice_ids = set(answer.question.options.values_list('id', flat=True))
        if not set(choice_ids).issubset(valid_choice_ids):
            return Response({'error': 'One or more choices are invalid for this question.'}, status=status.HTTP_400_BAD_REQUEST)

        answer.selected_choices.set(choice_ids)
        correct_ids = set(answer.question.options.filter(is_correct=True).values_list('id', flat=True))
        answer.is_correct = set(choice_ids) == correct_ids
        answer.save()

        return Response({'correct': answer.is_correct})

    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        session = get_object_or_404(MockTestSession, pk=pk, user=request.user)
        total = session.answers.count()
        correct = session.answers.filter(is_correct=True).count()
        wrong = total - correct

        session.score = round((correct / total) * 100)
        session.finished_at = timezone.now()
        session.save()

        # Update UserEvaluation
        profile = request.user.profile
        evaluation, _ = UserEvaluation.objects.get_or_create(user=profile)

        evaluation.QuestionAnswered = str(int(evaluation.QuestionAnswered or "0") + total)
        evaluation.CorrectAnswered = str(int(evaluation.CorrectAnswered or "0") + correct)
        evaluation.WrongAnswered = str(int(evaluation.WrongAnswered or "0") + wrong)
        evaluation.save(update_fields=['QuestionAnswered', 'CorrectAnswered', 'WrongAnswered'])

        return Response(MockTestResultSerializer(session).data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        sessions = MockTestSession.objects.filter(user=request.user, finished_at__isnull=False).order_by('-finished_at')
        return Response(MockTestResultSerializer(sessions, many=True).data)
'''

class MockTestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def start(self, request):
        total_questions = 24
        questions = list(Question.objects.filter(type="mockTest"))

        if len(questions) < total_questions:
            return Response({
                "success": False,
                "message": "Not enough questions to start the test.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        selected_questions = random.sample(questions, total_questions)
        session = MockTestSession.objects.create(user=request.user, total_questions=total_questions)

        answer_map = []
        for q in selected_questions:
            MockTestAnswer.objects.create(session=session, question=q)
            answer_map.append({
                "question_id": q.id,
                "question_text": q.question_text,  # fixed field name
                "image": q.image.url if q.image else None,
                "multiple_answers": q.multiple_answers,
                "options": list(q.options.values('id', 'text')),
            })

        # Update UserEvaluation
        profile = request.user.profile
        evaluation, _ = UserEvaluation.objects.get_or_create(user=profile)
        evaluation.MockTestTaken += 1
        evaluation.save(update_fields=['MockTestTaken'])

        return Response({
            "success": True,
            "message": "Mock test session started successfully.",
            "data": {
                "session_id": session.id,
                "questions": answer_map
            }
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        session = get_object_or_404(MockTestSession, pk=pk, user=request.user)
        answers = session.answers.select_related('question').prefetch_related('selected_choices', 'question__options')
        data = []
        for a in answers:
            data.append({
                'question': QuestionSerializer(a.question).data,
                'selected_choices': list(a.selected_choices.values_list('id', flat=True)),
                'is_correct': a.is_correct
            })
        
        return Response({
            "success": True,
            "message": "Mock test session retrieved successfully.",
            "data": {
                "session_id": session.id,
                "answers": data
            }
        })

    @action(detail=True, methods=['post'])
    def answer(self, request, pk=None):
        session = get_object_or_404(MockTestSession, pk=pk, user=request.user)
        question_id = request.data.get('question')
        choice_ids = request.data.get('selected_choice_ids', [])

        if question_id is None or not isinstance(choice_ids, list):
            return Response({
                "success": False,
                "message": 'Both "question" and "selected_choice_ids" are required.',
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            answer = MockTestAnswer.objects.get(session=session, question_id=question_id)
        except MockTestAnswer.DoesNotExist:
            return Response({
                "success": False,
                "message": 'Question not found in this session.',
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_choice_ids = set(answer.question.options.values_list('id', flat=True))
        if not set(choice_ids).issubset(valid_choice_ids):
            return Response({
                "success": False,
                "message": 'One or more choices are invalid for this question.',
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        answer.selected_choices.set(choice_ids)
        correct_ids = set(answer.question.options.filter(is_correct=True).values_list('id', flat=True))
        answer.is_correct = set(choice_ids) == correct_ids
        answer.save()

        return Response({
            "success": True,
            "message": 'Answer submitted successfully.',
            "data": {
                'correct': answer.is_correct
            }
        })

    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        session = get_object_or_404(MockTestSession, pk=pk, user=request.user)
        total = session.answers.count()
        correct = session.answers.filter(is_correct=True).count()
        wrong = total - correct

        session.score = round((correct / total) * 100)
        session.finished_at = timezone.now()
        session.save()

        # Update UserEvaluation
        profile = request.user.profile
        evaluation, _ = UserEvaluation.objects.get_or_create(user=profile)

        evaluation.QuestionAnswered = str(int(evaluation.QuestionAnswered or "0") + total)
        evaluation.CorrectAnswered = str(int(evaluation.CorrectAnswered or "0") + correct)
        evaluation.WrongAnswered = str(int(evaluation.WrongAnswered or "0") + wrong)
        evaluation.save(update_fields=['QuestionAnswered', 'CorrectAnswered', 'WrongAnswered'])

        return Response({
            "success": True,
            "message": "Mock test session finished successfully.",
            "data": MockTestResultSerializer(session).data
        })

    @action(detail=False, methods=['get'])
    def history(self, request):
        sessions = MockTestSession.objects.filter(user=request.user, finished_at__isnull=False).order_by('-finished_at')
        return Response({
            "success": True,
            "message": "Mock test history retrieved successfully.",
            "data": MockTestResultSerializer(sessions, many=True).data
        })

    @action(detail=True, methods=['post'])
    def submit_all_answers(self, request, pk=None):
        session = get_object_or_404(MockTestSession, pk=pk, user=request.user)
        submitted_answers = request.data.get('answers', [])

        if not isinstance(submitted_answers, list):
            return Response({
                "success": False,
                "message": 'Answers must be a list of question and choices.',
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        correct_count = 0
        total = session.answers.count()

        for item in submitted_answers:
            question_id = item.get('question')
            choice_ids = item.get('selected_choice_ids', [])

            if not question_id or not isinstance(choice_ids, list):
                continue  # Skip invalid item

            try:
                answer = MockTestAnswer.objects.get(session=session, question_id=question_id)
            except MockTestAnswer.DoesNotExist:
                continue

            valid_choices = set(answer.question.options.values_list('id', flat=True))
            if not set(choice_ids).issubset(valid_choices):
                continue

            answer.selected_choices.set(choice_ids)
            correct_ids = set(answer.question.options.filter(is_correct=True).values_list('id', flat=True))
            answer.is_correct = set(choice_ids) == correct_ids
            answer.save()

            if answer.is_correct:
                correct_count += 1

        # Finalize the session
        session.score = round((correct_count / total) * 100)
        session.finished_at = timezone.now()
        session.save()

        # Update evaluation
        profile = request.user.profile
        evaluation, _ = UserEvaluation.objects.get_or_create(user=profile)
        wrong_count = total - correct_count
        evaluation.QuestionAnswered = str(int(evaluation.QuestionAnswered or "0") + total)
        evaluation.CorrectAnswered = str(int(evaluation.CorrectAnswered or "0") + correct_count)
        evaluation.WrongAnswered = str(int(evaluation.WrongAnswered or "0") + wrong_count)
        evaluation.save(update_fields=['QuestionAnswered', 'CorrectAnswered', 'WrongAnswered'])

        return Response({
            "success": True,
            "message": "All answers submitted and test session finished.",
            "data": MockTestResultSerializer(session).data
        }, status=status.HTTP_200_OK)




class FreeMockTestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def start(self, request):
        total_questions = 24
        questions = list(Question.objects.filter(type="freeMockTest"))
        if len(questions) < total_questions:
            return Response({
                "success": False,
                "message": "Not enough questions to start the test.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        selected_questions = random.sample(questions, total_questions)
        session = FreeMockTestSession.objects.create(user=request.user, total_questions=total_questions)

        for q in selected_questions:
            FreeMockTestAnswer.objects.create(session=session, question=q)

        return Response({
            "success": True,
            "message": "Free mock test session started successfully.",
            "data": FreeStartMockTestSerializer(session).data
        })

    def retrieve(self, request, pk=None):
        session = get_object_or_404(FreeMockTestSession, pk=pk, user=request.user)
        answers = session.answers.select_related('question').prefetch_related('question__options')

        questions_data = []
        for answer in answers:
            question = answer.question
            options = question.options.all()
            questions_data.append({
                'question_id': question.id,
                'question_text': question.question_text,
                'image': question.image.url if question.image else None,
                'multiple_answers': question.multiple_answers,
                'options': [
                    {'id': opt.id, 'text': opt.text}
                    for opt in options
                ]
            })

        return Response({
            "success": True,
            "message": "Free mock test session retrieved successfully.",
            "data": {
                'session_id': session.id,
                'questions': questions_data
            }
        })

    @action(detail=True, methods=['post'])
    def answer(self, request, pk=None):
        session = get_object_or_404(FreeMockTestSession, pk=pk, user=request.user)
        question_id = request.data.get('question')
        choice_ids = request.data.get('selected_choice_ids', [])

        if question_id is None or not isinstance(choice_ids, list):
            return Response({
                "success": False,
                "message": 'Both "question" and "selected_choice_ids" are required and choice_ids must be a list.',
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            answer = FreeMockTestAnswer.objects.get(session=session, question_id=question_id)
        except FreeMockTestAnswer.DoesNotExist:
            return Response({
                "success": False,
                "message": 'Question not found in this session.',
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if choices belong to the question
        valid_choice_ids = set(answer.question.options.values_list('id', flat=True))
        if not set(choice_ids).issubset(valid_choice_ids):
            return Response({
                "success": False,
                "message": 'One or more selected choices are invalid for this question.',
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save selected choices
        answer.selected_choices.set(choice_ids)

        # Check correctness
        correct_ids = set(answer.question.options.filter(is_correct=True).values_list('id', flat=True))
        answer.is_correct = set(choice_ids) == correct_ids
        answer.save()

        return Response({
            "success": True,
            "message": 'Answer submitted successfully.',
            "data": {'correct': answer.is_correct}
        })

    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        session = get_object_or_404(FreeMockTestSession, pk=pk, user=request.user)
        total = session.answers.count()
        correct = session.answers.filter(is_correct=True).count()
        session.score = round((correct / total) * 100)
        session.finished_at = timezone.now()
        session.save()
        return Response({
            "success": True,
            "message": "Free mock test session finished successfully.",
            "data": FreeMockTestResultSerializer(session).data
        })

    @action(detail=False, methods=['get'])
    def history(self, request):
        sessions = FreeMockTestSession.objects.filter(user=request.user, finished_at__isnull=False).order_by('-finished_at')
        return Response({
            "success": True,
            "message": "Free mock test history retrieved successfully.",
            "data": FreeMockTestResultSerializer(sessions, many=True).data
        })

    @action(detail=True, methods=['post'])
    def submit_all_answers(self, request, pk=None):
        session = get_object_or_404(FreeMockTestSession, pk=pk, user=request.user)

        answers_data = request.data.get('answers', [])
        if not isinstance(answers_data, list):
            return Response({
                "success": False,
                "message": '"answers" must be a list.',
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        total = 0
        correct = 0
        detailed_results = []

        for item in answers_data:
            question_id = item.get('question')
            selected_ids = item.get('selected_choice_ids', [])

            if question_id is None or not isinstance(selected_ids, list):
                continue  # Skip invalid entries

            try:
                answer = FreeMockTestAnswer.objects.get(session=session, question_id=question_id)
            except FreeMockTestAnswer.DoesNotExist:
                continue

            valid_choice_ids = set(answer.question.options.values_list('id', flat=True))
            if not set(selected_ids).issubset(valid_choice_ids):
                continue

            answer.selected_choices.set(selected_ids)

            correct_ids = set(answer.question.options.filter(is_correct=True).values_list('id', flat=True))
            is_correct = set(selected_ids) == correct_ids
            answer.is_correct = is_correct
            answer.save()

            correct_choice_ids = list(answer.question.options.filter(is_correct=True).values_list('id', flat=True))

            total += 1
            if is_correct:
                correct += 1

            detailed_results.append({
                'question_id': answer.question.id,
                'question': answer.question.question_text,
                'selected_choices': selected_ids,
                'correct_choices': correct_choice_ids,
                'is_correct': is_correct
            })

        # Finalize session
        session.score = round((correct / total) * 100) if total else 0
        session.finished_at = timezone.now()
        session.save()

        return Response({
            'success': True,
            'message': 'All answers submitted and test session finished.',
            'data': {
                'session_id': session.id,
                'score': session.score,
                'total_questions': total,
                'correct_answers': correct,
                'wrong_answers': total - correct,
                'results': detailed_results
            }
        }, status=status.HTTP_200_OK)




# -----------------------Question upload-------------------------------

class UploadCSVAPIView(APIView):
    permission_classes = [permissions.IsAdminUser, ]

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get("file")
        if not csv_file:
            return Response({
                "success": False,
                "message": "CSV file is required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(decoded_file)

            with transaction.atomic():
                for row in reader:
                    chapter_id = row.get("chapter_id")
                    try:
                        chapter = Chapter.objects.get(id=chapter_id)
                    except Chapter.DoesNotExist:
                        return Response({
                            "success": False,
                            "message": f"Chapter with id {chapter_id} not found.",
                            "data": None
                        }, status=status.HTTP_400_BAD_REQUEST)

                    question = Question.objects.create(
                        chapter=chapter,
                        type=row.get("type", "practice"),
                        question_text=row.get("question_text"),
                        explanation=row.get("explanation", ""),
                        multiple_answers=row.get("multiple_answers", "false").lower() == "true"
                    )

                    # Dynamically parse options
                    for i in range(1, 10):  # Support up to 9 options
                        option_text = row.get(f"option_{i}_text")
                        if option_text:
                            is_correct = row.get(f"option_{i}_correct", "false").lower() == "true"
                            QuestionOption.objects.create(
                                question=question,
                                text=option_text,
                                is_correct=is_correct
                            )

            return Response({
                "success": True,
                "message": "Questions uploaded successfully.",
                "data": None
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "success": False,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
