from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import authenticate
from datetime import timedelta
import random

from main.models import Lesson, Chapter, Profile, GuidesSupport, HomePage, GuideSupportContent, LessonContent, UserEvaluation, Question, QuestionOption, MockTestSession, MockTestAnswer, FreeMockTestSession, FreeMockTestAnswer
from subscriptions.models import SubscriptionPlan, UserSubscription
from . serializers import LessonModelSerializers, ChapterModelSerializer, RegisterSerializer, ProfileModelSerializer, GuidesSupportModelSerializer, HomePageModelSerializer, GuideSupportContentModelSerializer, LessonContentModelSerializer, UserEvaluationModelSerializer, SubscriptionPlanSerializer, UserSubscriptionSerializer, QuestionOptionSerializer, QuestionSerializer, StartMockTestSerializer, MockTestAnswerSerializer, MockTestResultSerializer, FreeMockTestAnswerSerializer, FreeMockTestResultSerializer, FreeStartMockTestSerializer

from rest_framework.views import View, APIView
from rest_framework import mixins, generics, status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
import csv
from io import TextIOWrapper

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
    

class UserEvaluationView(APIView):
    def get(self, request):
        try:
            evaluation = UserEvaluation.objects.get(user=request.user.profile)
        except UserEvaluation.DoesNotExist:
            return Response({'error': 'Evaluation not found.'}, status=status.HTTP_404_NOT_FOUND)

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

        response_data = {
            "MockTestTaken": evaluation.MockTestTaken,
            "LeftMockTest": evaluation.LeftMockTest,
            "PracticeCompleted": evaluation.PracticeCompleted,
            "QuestionAnswered": total,
            "CorrectAnsweredPercentage": correct_percentage,
            "WrongAnsweredPercentage": wrong_percentage,
        }

        return Response(response_data, status=status.HTTP_200_OK)


        
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
    # authentication_classes = [TokenAuthentication]
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


class ChapterDetailsAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterModelSerializer
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
    GET /guide/<guide_id>/?step=0
    Returns 10 items per step (pagination)
    """
    PAGE_SIZE = 10

    def get(self, request, guide_id):
        try:
            step = int(request.query_params.get("step", 0))
        except (TypeError, ValueError):
            return Response({"detail": "step must be an integer."},
                            status=status.HTTP_400_BAD_REQUEST)

        guide = get_object_or_404(GuidesSupport, pk=guide_id)
        title = guide.title

        contents_qs = GuideSupportContent.objects.filter(
            guide_id=guide_id
        ).order_by("id")

        total = contents_qs.count()
        start = step * self.PAGE_SIZE
        end = start + self.PAGE_SIZE

        if start >= total:  
            return Response({"detail": "No content available for this page."},
                            status=status.HTTP_404_NOT_FOUND)

        current_items = contents_qs[start:end]
        serializer = GuideSupportContentModelSerializer(current_items, many=True)

        return Response({
            "title": title,
            "total_items": total,
            "content": serializer.data,
        }, status=status.HTTP_200_OK)




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



#-------------------------------------Practice Chapter view-------------------------------------


class PracticeChapterList(APIView):
    def get(self, request):
        chapters = Chapter.objects.all()
        serializer = ChapterModelSerializer(chapters, many=True)
        return Response(serializer.data)



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
            return Response({"detail": "step must be an integer."},
                            status=status.HTTP_400_BAD_REQUEST)

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
            question = Question.objects.get(id=question_id, chapter_id=chapter_id)
        except Question.DoesNotExist:
            return Response({"detail": "Invalid question."}, status=status.HTTP_400_BAD_REQUEST)

        correct_set = set(question.options.filter(is_correct=True).values_list('id', flat=True))
        is_correct  = selected_options == correct_set

        # ----- you can persist attempt here if you wish -----

        # Prepare result for this question
        question_result = {
            "question_id": question_id,
            "is_correct":  is_correct,
            "correct_options": list(correct_set),
            "selected_options": list(selected_options),
            "explanation": question.explanation,
        }

        # Determine next step
        qs    = Question.objects.filter(chapter_id=chapter_id).order_by("id")
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
            "next_question": {
                "step": next_step,
                "total": total,
                "question": next_ser.data,
                "has_next": next_step < total - 1,
                "has_prev": True
            }
        }, status=status.HTTP_200_OK)


# ________-----------------------Mock Test-----------------______________

from django.db.models import Max
class MockTestHomeViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        latest_session = MockTestSession.objects.filter(user=user).order_by('-started_at').first()
        total_questions = latest_session.total_questions if latest_session else 24
        duration_minutes = latest_session.duration_minutes if latest_session else 45

        total_tests = MockTestSession.objects.filter(user=user, finished_at__isnull=False).count()
        best_score = MockTestSession.objects.filter(
            user=user, finished_at__isnull=False, score__isnull=False
        ).aggregate(Max('score'))['score__max'] or 0

        return Response({
            "total_questions": total_questions,
            "duration_minutes": duration_minutes,
            "total_tests_taken": total_tests,
            "best_score": best_score
        })



class MockTestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def start(self, request):
        total_questions = 14
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



class FreeMockTestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def start(self, request):
        total_questions = 14
        questions = list(Question.objects.filter(type = "freeMockTest"))
        if len(questions) < total_questions:
            return Response({'error': 'Not enough questions to start the test.'}, status=status.HTTP_400_BAD_REQUEST)

        selected_questions = random.sample(questions, total_questions)
        session = FreeMockTestSession.objects.create(user=request.user, total_questions=total_questions)

        for q in selected_questions:
            FreeMockTestAnswer.objects.create(session=session, question=q)

        return Response(FreeStartMockTestSerializer(session).data)

    def retrieve(self, request, pk=None):
        session = get_object_or_404(FreeMockTestSession, pk=pk, user=request.user)
        answers = session.answers.select_related('question').prefetch_related('selected_choices', 'question__options')

        data = []
        for answer in answers:
            data.append({
                'question': QuestionSerializer(answer.question).data,
                'selected_choices': list(answer.selected_choices.values_list('id', flat=True)),
                'is_correct': answer.is_correct
            })
        return Response({'session_id': session.id, 'answers': data})

    @action(detail=True, methods=['post'])
    def answer(self, request, pk=None):
        session = get_object_or_404(FreeMockTestSession, pk=pk, user=request.user)
        question_id = request.data.get('question')
        choice_ids = request.data.get('selected_choice_ids', [])

        if question_id is None or not isinstance(choice_ids, list):
            return Response({'error': 'Both "question" and "selected_choice_ids" are required and choice_ids must be a list.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            answer = FreeMockTestAnswer.objects.get(session=session, question_id=question_id)
        except FreeMockTestAnswer.DoesNotExist:
            return Response({'error': 'Question not found in this session.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if choices belong to the question
        valid_choice_ids = set(answer.question.options.values_list('id', flat=True))
        if not set(choice_ids).issubset(valid_choice_ids):
            return Response({'error': 'One or more selected choices are invalid for this question.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Save selected choices
        answer.selected_choices.set(choice_ids)

        # Check correctness
        correct_ids = set(answer.question.options.filter(is_correct=True).values_list('id', flat=True))
        answer.is_correct = set(choice_ids) == correct_ids
        answer.save()

        return Response({'correct': answer.is_correct})

    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        session = get_object_or_404(FreeMockTestSession, pk=pk, user=request.user)
        total = session.answers.count()
        correct = session.answers.filter(is_correct=True).count()
        session.score = round((correct / total) * 100)
        session.finished_at = timezone.now()
        session.save()
        return Response(FreeMockTestResultSerializer(session).data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        sessions = FreeMockTestSession.objects.filter(user=request.user, finished_at__isnull=False).order_by('-finished_at')
        return Response(FreeMockTestResultSerializer(sessions, many=True).data)
    


    # -----------------------Question upload-------------------------------

class UploadCSVAPIView(APIView):
    permission_classes = [permissions.IsAdminUser, ]

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get("file")
        if not csv_file:
            return Response({"error": "CSV file is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(decoded_file)

            with transaction.atomic():
                for row in reader:
                    chapter_id = row.get("chapter_id")
                    try:
                        chapter = Chapter.objects.get(id=chapter_id)
                    except Chapter.DoesNotExist:
                        return Response({"error": f"Chapter with id {chapter_id} not found."}, status=status.HTTP_400_BAD_REQUEST)

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

            return Response({"message": "Questions uploaded successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
