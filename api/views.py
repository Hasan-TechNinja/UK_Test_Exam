from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import authenticate
from datetime import timedelta
import random
from django.db.models import Max
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError as DjangoValidationError

from main.models import GuidesSupportGlossary, Lesson, Chapter, Profile, GuidesSupport, HomePage, GuideSupportContent, LessonContent, QuestionGlossary, UserEvaluation, Question, QuestionOption, MockTestSession, MockTestAnswer, FreeMockTestSession, FreeMockTestAnswer, ChapterProgress, LessonProgress, Glossary
from subscriptions.models import SubscriptionPlan, UserSubscription
from . serializers import LessonModelSerializers, ChapterModelSerializer, QuestionForTestSerializer, RegisterSerializer, ProfileModelSerializer, GuidesSupportModelSerializer, HomePageModelSerializer, GuideSupportContentModelSerializer, LessonContentModelSerializer, UserEvaluationModelSerializer, SubscriptionPlanSerializer, UserSubscriptionSerializer, QuestionOptionSerializer, QuestionSerializer, StartMockTestSerializer, MockTestAnswerSerializer, MockTestResultSerializer, FreeMockTestAnswerSerializer, FreeMockTestResultSerializer, FreeStartMockTestSerializer

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
from django.db.models import Prefetch
from collections import defaultdict

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

        if user.first_name and user.last_name:
                name = f"{user.first_name} {user.last_name}"
        elif user.email:
            name = user.email
        else:
            name = user.username

        send_mail(
            subject='Password Reset Request',
            message=(
                f"Hello, {name}\n"
                "We received a request to reset your account password.\n"
                f"Your password reset code is: "
                f"{code}\n\n"
                "If you did not request this, please ignore this email.\n"
                # "For security, this code will expire in 10 minutes.\n\n"
                "Best regards,\n"
                "The Life In The UK Team"
            ),
            from_email='noreply@example.com',
            recipient_list=[email],
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
        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "User not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            # It's safer to fetch by both user and code to avoid a separate equality check
            reset = PasswordResetCode.objects.get(user=user, code=code)
        except PasswordResetCode.DoesNotExist:
            return Response({
                "success": False,
                "message": "Invalid or missing reset code.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        if reset.is_expired():
            reset.delete()
            return Response({
                "success": False,
                "message": "Reset code expired.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate password and handle validation errors
        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as e:
            return Response({
                "success": False,
                "message": "Password validation failed.",
                "errors": e.messages,  # e.g. ["The password is too similar to the username."]
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update password
        user.set_password(new_password)
        user.save()
        reset.delete()

        return Response({
            "success": True,
            "message": "Password reset successful.",
            "data": None
        }, status=status.HTTP_200_OK)



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
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            "success": True,
            "message": "Home page data fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "success": True,
            "message": "Profile updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class QuestionAdminView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "success": True,
            "message": "Questions fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "success": True,
            "message": "Question created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class QuestionOptionAdminView(generics.ListCreateAPIView):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "success": True,
            "message": "Question options fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "success": True,
            "message": "Question option created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

class LessonAdminView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonModelSerializers
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "success": True,
            "message": "Lessons fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "success": True,
            "message": "Lesson created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    
class LessonContentAdminView(generics.ListCreateAPIView):
    queryset = LessonContent.objects.all()
    serializer_class = LessonContentModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "success": True,
            "message": "Lesson contents fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "success": True,
            "message": "Lesson content created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class ChapterAdminView(generics.ListCreateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "success": True,
            "message": "Chapters fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "success": True,
            "message": "Chapter created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class GuideSupportAdminView(generics.ListCreateAPIView):
    queryset = GuidesSupport.objects.all()
    serializer_class = GuidesSupportModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "success": True,
            "message": "Guide support entries fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "success": True,
            "message": "Guide support entry created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class GuideSupportContentAdminView(generics.ListCreateAPIView):
    queryset = GuideSupportContent.objects.all()
    serializer_class = GuideSupportContentModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "success": True,
            "message": "Guide support contents fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "success": True,
            "message": "Guide support content created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class SubscriptionPlanAdminView(generics.ListCreateAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "success": True,
            "message": "Subscription plans fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "success": True,
            "message": "Subscription plan created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
class StudentView(APIView):
    def get(self, request):
        student = len(User.objects.filter(is_staff=False, is_superuser=False))
        return Response({
            "success": True,
            "message": "Student count fetched successfully.",
            "data": {
                "student_count": student
            }
        }, status=status.HTTP_200_OK)


class ChapterCountView(APIView):
    def get(self, request):
        chapter = Chapter.objects.count()
        return Response({
            "success": True,
            "message": "Chapter count fetched successfully.",
            "data": {
                "chapter_count": chapter
            }
        }, status=status.HTTP_200_OK)


class LessonCountView(APIView):
    def get(self, request):
        lesson = Lesson.objects.count()
        return Response({
            "success": True,
            "message": "Lesson count fetched successfully.",
            "data": {
                "lesson_count": lesson
            }
        }, status=status.HTTP_200_OK)
    

class MockTestCount(APIView):
    def get(self, request):
        mock_test = MockTestAnswer.objects.count()
        return Response({
            "success": True,
            "message": "Mock test count fetched successfully.",
            "data": {
                "mock_test_count": mock_test
            }
        }, status=status.HTTP_200_OK)


class UserSubscriptionCount(APIView):
    def get(self, request):
        user_subscription = UserSubscription.objects.filter(is_active=True).count()
        return Response({
            "success": True,
            "message": "User subscription count fetched successfully.",
            "data": {
                "user_subscription_count": user_subscription
            }
        }, status=status.HTTP_200_OK)

# --------------------------------------------------Admin details view--------------------------------------s

class HomePageDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HomePage.objects.all()
    serializer_class = HomePageModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Home page details fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)  # to handle PATCH vs PUT
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Home page updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Home page deleted successfully.",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)

class ChapterDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Chapter details fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)  # support PATCH vs PUT
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Chapter updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Chapter deleted successfully.",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)


class LessonAdminDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonModelSerializers
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Lesson details fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Lesson updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Lesson deleted successfully.",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)

class LessonDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonModelSerializers
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Lesson details fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Lesson updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Lesson deleted successfully.",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)


class LessonContentDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LessonContent.objects.all()
    serializer_class = LessonContentModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Lesson content details fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Lesson content updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Lesson content deleted successfully.",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)


class QuestionDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Question details fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Question updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Question deleted successfully.",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)

class QuestionOptionDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Question option details fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Question option updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Question option deleted successfully.",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)


class GuideSupportDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GuidesSupport.objects.all()
    serializer_class = GuidesSupportModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Guide support details fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Guide support updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Guide support deleted successfully.",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)

class GuideSupportContentDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GuideSupportContent.objects.all()
    serializer_class = GuideSupportContentModelSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Guide support content details fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Guide support content updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Guide support content deleted successfully.",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)
class SubscriptionPlanDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Subscription plan details fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Subscription plan updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Subscription plan deleted successfully.",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)

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

        content_data = []
        for item in current_items:
            content_data.append({
                "id": item.id,
                "image": request.build_absolute_uri(item.image.url) if item.image else None,
                "description": item.description,
                "video": item.video,
                "created": item.created,
                "glossary_list": [
                    {
                        "id": g.id,
                        "title": g.title,
                        "description": g.description,
                    }
                    for g in item.glossaries.all()  # ✅ fixed
                ]
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
    Returns all practice questions in a chapter with options, correct answers, and question-specific glossaries
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, chapter_id):
        questions = (
            Question.objects
            .filter(type="practice", chapter_id=chapter_id)
            .order_by("id")
            .prefetch_related(
                Prefetch("options", queryset=QuestionOption.objects.order_by("id")),
                Prefetch("glossary", queryset=QuestionGlossary.objects.order_by("id")),
            )
        )

        serialized = QuestionSerializer(questions, many=True).data
        return Response({
            "success": True,
            "message": "Practice questions retrieved successfully.",
            "data": {
                "total": len(serialized),
                "questions": serialized
            }
        }, status=status.HTTP_200_OK)



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



class MockTestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get', 'post'])
    def start(self, request):
        total_questions = 24

        qs = (
            Question.objects
            .filter(type="mockTest")
            .prefetch_related(
                Prefetch("options", queryset=QuestionOption.objects.order_by("id")),
                Prefetch("glossary", queryset=QuestionGlossary.objects.order_by("id")),
            )
        )

        questions = list(qs)
        if len(questions) < total_questions:
            return Response({
                "success": False,
                "message": "Not enough questions to start the test.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        selected_questions = random.sample(questions, total_questions)
        session = MockTestSession.objects.create(user=request.user, total_questions=total_questions)

        MockTestAnswer.objects.bulk_create([
            MockTestAnswer(session=session, question=q) for q in selected_questions
        ])

        serialized = QuestionForTestSerializer(
            selected_questions, many=True, context={"request": request}
        ).data

        # update evaluation
        profile = request.user.profile
        evaluation, _ = UserEvaluation.objects.get_or_create(user=profile)
        evaluation.MockTestTaken += 1
        evaluation.save(update_fields=['MockTestTaken'])

        return Response({
            "success": True,
            "message": "Mock test session started successfully.",
            "data": {
                "session_id": session.id,
                "questions": serialized
            }
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        session = get_object_or_404(MockTestSession, pk=pk, user=request.user)

        answers = (
            session.answers
            .select_related("question")
            .prefetch_related(
                "selected_choices",
                Prefetch("question__options", queryset=QuestionOption.objects.order_by("id")),
                Prefetch("question__glossary", queryset=QuestionGlossary.objects.order_by("id")),
            )
        )

        data = []
        for a in answers:
            data.append({
                "question": QuestionForTestSerializer(a.question, context={"request": request}).data,
                "selected_choices": list(a.selected_choices.values_list("id", flat=True)),
                "is_correct": a.is_correct
            })

        return Response({
            "success": True,
            "message": "Mock test session retrieved successfully.",
            "data": {
                "session_id": session.id,
                "answers": data
            }
        }, status=status.HTTP_200_OK)

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
                "message": 'Answers must be a list of question_id and selected_options.',
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        correct_count = 0
        total = session.answers.count()

        for item in submitted_answers:
            question_id = item.get('question_id')
            choice_ids = item.get('selected_options', [])

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

    @action(detail=False, methods=['get', 'post'])
    def start(self, request):
        total_questions = 24

        qs = (
            Question.objects
            .filter(type="freeMockTest")
            .prefetch_related(
                Prefetch("options", queryset=QuestionOption.objects.order_by("id")),
                Prefetch("glossary", queryset=QuestionGlossary.objects.order_by("id")),
            )
        )
        questions = list(qs)

        if len(questions) < total_questions:
            return Response({
                "success": False,
                "message": "Not enough questions to start the test.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        selected_questions = random.sample(questions, total_questions)
        session = FreeMockTestSession.objects.create(user=request.user, total_questions=total_questions)

        # create answer rows
        FreeMockTestAnswer.objects.bulk_create([
            FreeMockTestAnswer(session=session, question=q) for q in selected_questions
        ])

        # serialize questions WITH correct answers (and pass request to render absolute image URLs)
        serialized_questions = QuestionForTestSerializer(
            selected_questions, many=True, context={"request": request}
        ).data

        return Response({
            "success": True,
            "message": "Free mock test session started successfully.",
            "data": {
                "session_id": session.id,
                "total_questions": total_questions,
                "duration_minutes": session.duration_minutes,
                "started_at": session.started_at,
                "questions": serialized_questions
            }
        }, status=status.HTTP_200_OK)
    


    def retrieve(self, request, pk=None):
        session = get_object_or_404(FreeMockTestSession, pk=pk, user=request.user)

        # load questions + options in one go
        answers = (
            session.answers
            .select_related("question")
            .prefetch_related(
                Prefetch("question__options", queryset=QuestionOption.objects.order_by("id")),
                Prefetch("question__glossary", queryset=QuestionGlossary.objects.order_by("id")),
            )
        )

        questions = [a.question for a in answers]
        questions_data = QuestionForTestSerializer(questions, many=True, context={"request": request}).data

        return Response({
            "success": True,
            "message": "Free mock test session retrieved successfully.",
            "data": {
                "session_id": session.id,
                "questions": questions_data
            }
        }, status=status.HTTP_200_OK)
    
    

    @action(detail=True, methods=['post'])
    def answer(self, request, pk=None):
        session = get_object_or_404(FreeMockTestSession, pk=pk, user=request.user)
        question_id = request.data.get('question_id')
        choice_ids = request.data.get('selected_options', [])

        if question_id is None or not isinstance(choice_ids, list):
            return Response({
                "success": False,
                "message": 'Both "question_id" and "selected_options" are required.',
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
            question_id = item.get('question_id')
            selected_ids = item.get('selected_options', [])

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

            correct_choice_ids = list(correct_ids)

            total += 1
            if is_correct:
                correct += 1

            detailed_results.append({
                'question_id': answer.question.id,
                'question': answer.question.question_text,
                'selected_options': selected_ids,
                'correct_options': correct_choice_ids,
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
        chapter_id = request.data.get("chapter_id")
        lesson_id = request.data.get("lesson_id")  # optional, if you have lesson
        question_type = request.data.get("type", "practice")

        if not csv_file or not chapter_id:
            return Response({
                "success": False,
                "message": "CSV file and chapter selection are required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            chapter = Chapter.objects.get(id=chapter_id)
        except Chapter.DoesNotExist:
            return Response({
                "success": False,
                "message": f"Chapter with id {chapter_id} not found.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(decoded_file)

            with transaction.atomic():
                for row in reader:
                    question = Question.objects.create(
                        chapter=chapter,
                        type=question_type,
                        question_text=row.get("question_text"),
                        explanation=row.get("explanation", ""),
                        multiple_answers="," in row.get("correct_answer", "")
                    )

                    correct_answers = [c.strip().lower() for c in row.get("correct_answer", "").split(",")]

                    for key, value in row.items():
                        if key.startswith("option_") and value:
                            option_text = value.strip()
                            # Match by either option text OR option key
                            is_correct = key.lower() in correct_answers or option_text.lower() in correct_answers
                            QuestionOption.objects.create(
                                question=question,
                                text=option_text,
                                is_correct=is_correct
                            )

                    # Parse glossary (only one per question now)
                    glossary_title = row.get("glossary_title")
                    glossary_description = row.get("glossary_description")
                    if glossary_title:
                        QuestionGlossary.objects.create(
                            question=question,
                            title=glossary_title.strip(),
                            description=glossary_description or ""
                        )

            return Response({
                "success": True,
                "message": "Questions with glossary uploaded successfully.",
                "data": None
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "success": False,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)


        
# ------------------------Lesson content & glossary upload csv --------------------------------

class ImportLessonContentCSVView(APIView):
    """
    POST multipart/form-data:
      - chapter_id (int)
      - lesson_id (int)
      - file (CSV file with headers like: description,video,glossary_title,glossary_description,...)

    Notes:
    - Admin selects Chapter and Lesson from UI, so CSV only needs content & glossary fields.
    - Glossary pairs (title, description) can repeat in any number of columns.
    """
    permission_classes = [permissions.IsAdminUser]

    REQUIRED_BASE_FIELDS = ["description", "video"]
    GLOSSARY_TITLE = "glossary_title"
    GLOSSARY_DESC = "glossary_description"

    def post(self, request):
        chapter_id = request.data.get("chapter_id")
        lesson_id = request.data.get("lesson_id")

        if not (chapter_id and lesson_id):
            return Response(
                {"detail": "chapter_id and lesson_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate lesson exists
        try:
            lesson = Lesson.objects.get(id=lesson_id, chapter_id=chapter_id)
        except Lesson.DoesNotExist:
            return Response(
                {"detail": "Invalid chapter_id or lesson_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        upload = request.FILES.get("file")
        if not upload:
            return Response({"detail": "Please attach a CSV file."},
                            status=status.HTTP_400_BAD_REQUEST)

        file_obj = TextIOWrapper(upload.file, encoding="utf-8-sig", newline="")

        sample = file_obj.read(4096)
        file_obj.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ","

        reader = csv.reader(file_obj, delimiter=delimiter)

        try:
            header = next(reader)
        except StopIteration:
            return Response({"detail": "CSV is empty."}, status=status.HTTP_400_BAD_REQUEST)

        norm_header = [h.strip().lower() for h in header]

        # Validate required base fields
        missing = [f for f in self.REQUIRED_BASE_FIELDS if f not in norm_header]
        if missing:
            return Response(
                {"detail": f"Missing required columns: {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        idx = {name: norm_header.index(name) for name in self.REQUIRED_BASE_FIELDS}

        # Glossary columns
        g_title_idxs = [i for i, h in enumerate(norm_header) if h == self.GLOSSARY_TITLE]
        g_desc_idxs  = [i for i, h in enumerate(norm_header) if h == self.GLOSSARY_DESC]
        glossary_pairs = list(zip(g_title_idxs, g_desc_idxs))

        created_counts = {"lesson_contents": 0, "glossaries": 0}
        errors = []

        @transaction.atomic
        def process_rows():
            nonlocal created_counts

            for row_num, row in enumerate(reader, start=2):
                if len(row) < len(norm_header):
                    row = row + [""] * (len(norm_header) - len(row))

                description = (row[idx["description"]]).strip()
                video       = (row[idx["video"]]).strip()

                if not description:
                    errors.append({"row": row_num, "error": "description is required"})
                    continue

                try:
                    lc = LessonContent.objects.create(
                        lesson=lesson,
                        description=description,
                        video=video or None,
                        image="lesson/default.png",  # optional fallback
                    )
                    created_counts["lesson_contents"] += 1
                except Exception as e:
                    errors.append({"row": row_num, "error": f"LessonContent create failed: {e}"})
                    continue

                # Glossaries
                glossaries = []
                for ti, di in glossary_pairs:
                    g_title = row[ti].strip() if ti < len(row) else ""
                    g_desc  = row[di].strip() if di < len(row) else ""
                    if g_title:
                        glossaries.append(Glossary(
                            lesson_content=lc,
                            title=g_title,
                            description=g_desc,
                        ))

                if glossaries:
                    Glossary.objects.bulk_create(glossaries)
                    created_counts["glossaries"] += len(glossaries)

        try:
            process_rows()
        except Exception as e:
            return Response(
                {"detail": "Import failed", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "message": "Lesson content imported successfully.",
                "data": created_counts,
                # "errors": errors,
            },
            status=status.HTTP_201_CREATED,
        )



class ImportGuideSupportCSVView(APIView):
    """
    POST multipart/form-data:
      - guide_id (int)
      - file (CSV)

    CSV headers:
      - Base (required): description, video
      - Glossary (repeatable): glossary_title, glossary_description, glossary_title, glossary_description, ...

    Behavior:
      - Creates ONE GuideSupportContent per CSV row (linked to the provided guide_id).
      - For each row, reads any number of (title, description) glossary pairs and creates them.
    """
    permission_classes = [permissions.IsAdminUser]

    REQUIRED_BASE_FIELDS = ["description", "video"]
    GLOSSARY_TITLE = "glossary_title"
    GLOSSARY_DESC = "glossary_description"

    def post(self, request):
        guide_id = request.data.get("guide_id")
        if not guide_id:
            return Response({"detail": "guide_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        guide = get_object_or_404(GuidesSupport, id=guide_id)

        upload = request.FILES.get("file")
        if not upload:
            return Response({"detail": "Please attach a CSV file."}, status=status.HTTP_400_BAD_REQUEST)

        # Robust decoding; handles BOM too
        file_obj = TextIOWrapper(upload.file, encoding="utf-8-sig", newline="")

        # Try to detect delimiter
        sample = file_obj.read(4096)
        file_obj.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ","

        reader = csv.reader(file_obj, delimiter=delimiter)

        # Header
        try:
            header = next(reader)
        except StopIteration:
            return Response({"detail": "CSV is empty."}, status=status.HTTP_400_BAD_REQUEST)

        norm_header = [h.strip().lower() for h in header]

        # Validate required base fields
        missing = [f for f in self.REQUIRED_BASE_FIELDS if f not in norm_header]
        if missing:
            return Response(
                {"detail": f"Missing required columns: {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Index map for base fields
        idx = {name: norm_header.index(name) for name in self.REQUIRED_BASE_FIELDS}

        # Collect all glossary_title and glossary_description column indices
        g_title_idxs = [i for i, h in enumerate(norm_header) if h == self.GLOSSARY_TITLE]
        g_desc_idxs  = [i for i, h in enumerate(norm_header) if h == self.GLOSSARY_DESC]

        # Pair them in order; extra unmatched columns (if any) are ignored
        glossary_pairs = list(zip(g_title_idxs, g_desc_idxs))

        created_counts = {"guide_support_contents": 0, "glossaries": 0}
        errors = []

        @transaction.atomic
        def process_rows():
            nonlocal created_counts

            for row_num, row in enumerate(reader, start=2):  # 1-based header → first data row is 2
                # Pad short rows
                if len(row) < len(norm_header):
                    row = row + [""] * (len(norm_header) - len(row))

                description = (row[idx["description"]] or "").strip()
                video       = (row[idx["video"]] or "").strip()

                if not description:
                    errors.append({"row": row_num, "error": "description is required"})
                    continue

                # Create the content (image not provided by CSV; leave null)
                try:
                    content = GuideSupportContent.objects.create(
                        guide=guide,
                        description=description,
                        video=video or "",
                        # image stays NULL by default
                    )
                    created_counts["guide_support_contents"] += 1
                except Exception as e:
                    errors.append({"row": row_num, "error": f"GuideSupportContent create failed: {e}"})
                    continue

                # Create glossaries found in this row
                glossaries = []
                for ti, di in glossary_pairs:
                    g_title = (row[ti] if ti < len(row) else "") or ""
                    g_desc  = (row[di] if di < len(row) else "") or ""
                    g_title = g_title.strip()
                    g_desc  = g_desc.strip()

                    if g_title:  # title is the trigger to create a glossary
                        glossaries.append(
                            GuidesSupportGlossary(
                                guide=content,      # FK -> GuideSupportContent
                                title=g_title[:200],
                                description=g_desc[:500],
                            )
                        )

                if glossaries:
                    GuidesSupportGlossary.objects.bulk_create(glossaries)
                    created_counts["glossaries"] += len(glossaries)

        try:
            process_rows()
        except Exception as e:
            return Response({"detail": "Import failed", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "success": True,
                "message": "Guide support content imported successfully.",
                "data": created_counts,
                # "errors": errors,  # uncomment if you want to return per-row issues
            },
            status=status.HTTP_201_CREATED,
        )
