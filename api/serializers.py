from rest_framework import serializers
from main.models import Chapter, Lesson, Profile, GuidesSupport, UserEvaluation, HomePage, LessonContent, GuideSupportContent, QuestionOption, Question, MockTestSession, MockTestAnswer, FreeMockTestSession, FreeMockTestAnswer
from subscriptions.models import SubscriptionPlan, UserSubscription
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

from main.models import EmailVerification
from django.core.mail import send_mail
import random



class ChapterModelSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()
    class Meta:
        model = Chapter
        # fields = "__all__"
        exclude = ['created']
        # fields = ['id', 'name', 'description', 'created']

    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def get_title(self, obj):
        return f"Chapter {obj.id}"

    def get_lessons(self, obj):
        lesson_qs = obj.lesson_set.all().order_by('id')
        return [f"{i+1}" for i, _ in enumerate(lesson_qs)]

    def create(self, validated_data):
        return super().create(validated_data)
    

class LessonModelSerializers(serializers.ModelSerializer):
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Lesson
        exclude = ['created']

    def create(self, validated_data):
    
        return super().create(validated_data)

    
'''
# Registration serializer without email verification------------------>

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="This email is already in use.")]
    )
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user'''
    
User = get_user_model()
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="This email is already in use.")]
    )
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False  # User is inactive until email is verified
        )

        code = str(random.randint(100000, 999999))
        EmailVerification.objects.create(user=user, code=code)

        send_mail(
            'Your Verification Code',
            f'Your verification code is {code}',
            'noreply@example.com',
            [user.email],
            fail_silently=False
        )

        return user


class ProfileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ["user", "id", "created_at"]


class GuidesSupportModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuidesSupport
        exclude = ['created']


class GuideSupportContentModelSerializer(serializers.ModelSerializer):
    glossary_list = serializers.SerializerMethodField()

    class Meta:
        model = GuideSupportContent
        fields = ['id', 'image', 'description', 'video', 'created', 'glossary_list']

    def get_glossary_list(self, obj):
        return obj.get_glossary_string_list()



class UserEvaluationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEvaluation
        fields = "__all__"
        # exclude = ['user']



class HomePageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = ['title', 'description', 'image']



class LessonContentModelSerializer(serializers.ModelSerializer):
    chapter_name = serializers.CharField(source='lesson.chapter.name', read_only=True)
    glossary_list = serializers.SerializerMethodField()

    class Meta:
        model = LessonContent
        fields = ['id','chapter_name','lesson','image','description','video','glossary_list']

    def get_glossary_list(self, obj):
        return obj.get_glossary_string_list()



class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = QuestionOption
        fields = ['id', 'text']

class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)
    class Meta:
        model  = Question
        fields = ['id', 'question_text', 'image', 'multiple_answers', 'options']





class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model (basic details).
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """
    Serializer for the SubscriptionPlan model.
    """
    name_display = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'name_display', 'price', 'duration_days', 'features']

class UserSubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserSubscription model.
    Includes nested SubscriptionPlan details and user info.
    """
    plan = SubscriptionPlanSerializer(read_only=True) # Nested serializer for plan details
    user = UserSerializer(read_only=True) # Nested serializer for user details
    is_currently_active = serializers.BooleanField(read_only=True) # Read-only property

    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'plan', 'start_date', 'end_date', 'is_active', 'last_renewed', 'is_currently_active']
        read_only_fields = ['user', 'start_date', 'end_date', 'is_active', 'last_renewed']


class StartMockTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MockTestSession
        fields = ['id', 'total_questions', 'duration_minutes', 'started_at']

class MockTestAnswerSerializer(serializers.ModelSerializer):
    selected_choice_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = MockTestAnswer
        fields = ['question', 'selected_choice_ids']

class MockTestResultSerializer(serializers.ModelSerializer):
    correct = serializers.SerializerMethodField()
    wrong = serializers.SerializerMethodField()

    class Meta:
        model = MockTestSession
        fields = ['id', 'score', 'correct', 'wrong', 'started_at', 'finished_at']

    def get_correct(self, obj):
        return obj.answers.filter(is_correct=True).count()

    def get_wrong(self, obj):
        return obj.answers.filter(is_correct=False).count()
    

class FreeStartMockTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeMockTestSession
        fields = ['id', 'total_questions', 'duration_minutes', 'started_at']


class FreeMockTestAnswerSerializer(serializers.ModelSerializer):
    selected_choice_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = FreeMockTestAnswer
        fields = ['question', 'selected_choice_ids']

class FreeMockTestResultSerializer(serializers.ModelSerializer):
    correct = serializers.SerializerMethodField()
    wrong = serializers.SerializerMethodField()

    class Meta:
        model = FreeMockTestSession
        fields = ['id', 'score', 'correct', 'wrong', 'started_at', 'finished_at']

    def get_correct(self, obj):
        return obj.answers.filter(is_correct=True).count()

    def get_wrong(self, obj):
        return obj.answers.filter(is_correct=False).count()
