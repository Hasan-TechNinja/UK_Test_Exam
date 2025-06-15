from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import authenticate
from datetime import timedelta

from main.models import Question, Lesson, Chapter, Profile, GuidesSupport, HomePage, GuideSupportContent, LessonContent, UserEvaluation
from subscriptions.models import SubscriptionPlan, UserSubscription
from . serializers import LessonModelSerializers, QuestionModelSerializer, ChapterModelSerializer, RegisterSerializer, ProfileModelSerializer, GuidesSupportModelSerializer, HomePageModelSerializer, GuideSupportContentModelSerializer, LessonContentModelSerializer, UserEvaluationModelSerializer, SubscriptionPlanSerializer, UserSubscriptionSerializer
# from . permissions import IsAdminOrReadOnly

from rest_framework.views import View, APIView
from rest_framework import mixins, generics, status, viewsets
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.decorators import action

#  Create your views here.


# -----------------------------------------------Authentication section----------------------------------
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logout successfully'}, status=status.HTTP_200_OK)
    

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileModelSerializer

    def get_object(self):
        return self.request.user.profile

    
# --------------------------------------------------Admin Control---------------------------------------------

class HomePageAdminView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    queryset = HomePage.objects.all()
    serializer_class = HomePageModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class QuestionAdminView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class LessonAdminView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonModelSerializers
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    
    
class LessonContentAdminView(generics.ListCreateAPIView):
    queryset = LessonContent.objects.all()
    serializer_class = LessonContentModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class ChapterAdminView(generics.ListCreateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterModelSerializer
    permission_classes = [IsAdminUser]


class GuideSupportAdminView(generics.ListCreateAPIView):
    queryset = GuidesSupport.objects.all()
    serializer_class = GuidesSupportModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class GuideSupportContentAdminView(generics.ListCreateAPIView):
    queryset = GuideSupportContent.objects.all()
    serializer_class = GuideSupportContentModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class SubscriptionPlanAdminView(generics.ListCreateAPIView):
    queryset = SubscriptionPlan
    serializer_class = SubscriptionPlanSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


# --------------------------------------------------Admin details view--------------------------------------s
class QuestionDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionModelSerializer
    authentication_classes = [TokenAuthentication]
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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"


class ChapterDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

class GuideSupportDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GuidesSupport.objects.all()
    serializer_class = GuidesSupportModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

class GuideSupportContentDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GuidesSupport.objects.all()
    serializer_class = GuidesSupportModelSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

class SubscriptionPlanDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionPlan
    serializer_class = SubscriptionPlanSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

# --------------------------------------------------------Study section--------------------------------------

class HomePageView(APIView):
    def get(self, request):
        home = HomePage.objects.all()
        serializer = HomePageModelSerializer(home, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ChapterListView(APIView):
    def get(self, request):
        chapters = Chapter.objects.all().order_by('id')
        serializer = ChapterModelSerializer(chapters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 
    

class ChapterLessonsView(APIView):
    def get(self, request, pk):
        chapter = get_object_or_404(Chapter, id=pk)
        lessons = Lesson.objects.filter(chapter=chapter).reverse()
        serializer = LessonModelSerializers(lessons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class ChapterLessonDetailView(APIView):
    """
    GET http://127.0.0.1:8000/chapters/1/1/?step=0
    Each step returns 10 lesson contents
    """
    def get(self, request, chapter_id, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id, chapter_id=chapter_id)

        # Parse step (pagination)
        try:
            step = int(request.query_params.get('step', 0))
        except (TypeError, ValueError):
            return Response({"detail": "Invalid step value"}, status=status.HTTP_400_BAD_REQUEST)

        PAGE_SIZE = 10
        start_index = step * PAGE_SIZE
        end_index = start_index + PAGE_SIZE

        lesson_qs = LessonContent.objects.filter(lesson=lesson).order_by('id')
        total = lesson_qs.count()

        if start_index >= total:
            return Response({"detail": "No content available for this page."}, status=status.HTTP_404_NOT_FOUND)

        # Slice queryset for the current page
        current_page_items = lesson_qs[start_index:end_index]
        serializer = LessonContentModelSerializer(current_page_items, many=True)

        return Response({
            "step": step,
            # "page_size": PAGE_SIZE,
            "total_items": total,
            # "has_next": end_index < total,
            # "has_prev": start_index > 0,
            "content": serializer.data
        }, status=status.HTTP_200_OK)


    
# -----------------------------------------------------Guides & Support section-------------------------------------
    
class GuideSupportView(APIView):
    """
    GET /api/guides/
    """
    def get(self, request):
        guides = GuidesSupport.objects.all().order_by('id')
        serializer = GuidesSupportModelSerializer(guides, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GuideSupportContentView(APIView):
    """
    GET http://127.0.0.1:8000/guide/1/?step=0
    Returns 10 items per step (pagination)
    """
    def get(self, request, guide_id):
        try:
            step = int(request.query_params.get("step", 0))
        except (TypeError, ValueError):
            return Response({"detail": "step must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        PAGE_SIZE = 10
        start_index = step * PAGE_SIZE
        end_index = start_index + PAGE_SIZE

        # Get paginated contents
        contents = GuideSupportContent.objects.filter(guide_id=guide_id).order_by("id")
        total = contents.count()

        if start_index >= total:
            return Response({"detail": "No content available for this page."}, status=status.HTTP_404_NOT_FOUND)

        current_items = contents[start_index:end_index]
        serializer = GuideSupportContentModelSerializer(current_items, many=True)

        return Response({
            # "step": step,
            # "page_size": PAGE_SIZE,
            "total_items": total,
            # "has_prev": start_index > 0,
            # "has_next": end_index < total,
            "content": serializer.data
        }, status=status.HTTP_200_OK)


#----------------------------------------------User profile section-----------------------

class UserEvaluationView(APIView):
    def get(self, request, pk):
        evaluation = UserEvaluation.objects.get(user = request.user)
        serializer = UserEvaluationModelSerializer(evaluation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



# -----------------------------------Subscription----------------


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows subscription plans to be viewed.
    Accessible to anyone.
    """
    queryset = SubscriptionPlan.objects.all().order_by('price')
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny] # Anyone can see the available plans

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
            user_subscription = self.get_queryset().get() # Should be OneToOne, so get() works
            serializer = self.get_serializer(user_subscription)
            return Response(serializer.data)
        except UserSubscription.DoesNotExist:
            return Response({"message": "No active subscription found for this user."},
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        """
        Allows a user to subscribe to a specific plan.
        This endpoint would typically integrate with a payment gateway.
        For this tutorial, we'll simulate a successful payment.
        """
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({"error": "Plan ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Subscription plan not found."}, status=status.HTTP_404_NOT_FOUND)


        with transaction.atomic(): # Ensure atomicity of database operations
            user_subscription, created = UserSubscription.objects.get_or_create(user=request.user)

            # Update subscription details
            user_subscription.plan = plan
            user_subscription.is_active = True
            user_subscription.start_date = timezone.now() # Reset start date for new subscription/renewal
            user_subscription.last_renewed = timezone.now()

            # Calculate end_date based on plan duration
            if plan.duration_days:
                user_subscription.end_date = user_subscription.start_date + timedelta(days=plan.duration_days)
            else:
                user_subscription.end_date = None # Lifetime access

            user_subscription.save()

            serializer = self.get_serializer(user_subscription)
            return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def cancel(self, request):
        """
        Allows a user to cancel their active subscription.
        Does not refund, just deactivates the subscription.
        """
        try:
            user_subscription = self.get_queryset().get()
            if not user_subscription.is_active:
                return Response({"message": "Subscription is already inactive."},
                                status=status.HTTP_400_BAD_REQUEST)

            user_subscription.is_active = False
            user_subscription.save()
            serializer = self.get_serializer(user_subscription)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserSubscription.DoesNotExist:
            return Response({"message": "No active subscription found to cancel."},
                            status=status.HTTP_404_NOT_FOUND)
