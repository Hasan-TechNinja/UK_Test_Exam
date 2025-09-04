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
import json



class ChapterModelSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()
    class Meta:
        model = Chapter
        # fields = "__all__"
        # exclude = ['created']
        fields = ['id', 'name', 'description', 'lessons']

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



from django.utils.text import slugify

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="This email is already in use.")]
    )
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'password']  # Removed username input

    def create(self, validated_data):
        email = validated_data['email']
        username_base = slugify(email.split('@')[0])
        username = username_base

        # Ensure uniqueness
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            is_active=False
        )

        code = str(random.randint(100000, 999999))
        EmailVerification.objects.create(user=user, code=code)

        send_mail(
            subject='Your Register Verification Code',
            message=(
                f"Hello {email},\n\n"
                "Thank you for registering with us.\n"
                f"Your verification code is: {code}\n\n"
                "Please use this code to verify your account.\n"
                "If you did not request this, please ignore this email.\n\n"
                "Best regards,\n"
                "The Life In The UK Team"
            ),
            from_email='noreply@example.com',
            recipient_list=[email],
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
    glossary = serializers.SerializerMethodField()

    class Meta:
        model = LessonContent
        fields = ['id', 'chapter_name', 'lesson', 'image', 'description', 'video', 'glossary']

    def get_glossary(self, obj):
        try:
            data = json.loads(obj.glossary)
            # Ensure it's in the right format: list of dicts
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                return data
            # fallback if it's a dict
            if isinstance(data, dict):
                return [data]
        except Exception:
            # fallback for "title:desc,title2:desc2"
            items = [item.strip() for item in obj.glossary.split(',') if item.strip()]
            return [{f"title {i+1}": val} for i, val in enumerate(items)]
        return []
    
class LessonContentModelSerializer(serializers.ModelSerializer):
    chapter_name = serializers.CharField(source='lesson.chapter.name', read_only=True)

    class Meta:
        model = LessonContent
        fields = ['id', 'chapter_name', 'lesson', 'image', 'description', 'video', 'glossary']


'''
class LessonContentModelSerializer(serializers.ModelSerializer):
    chapter_name = serializers.CharField(source='lesson.chapter.name', read_only=True)

    class Meta:
        model = LessonContent
        fields = ['id', 'chapter_name', 'lesson', 'image', 'description', 'video', 'glossary']

'''



class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = QuestionOption
        fields = ['id', 'text']

class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)
    correct_option_ids = serializers.SerializerMethodField()
    correct_option_texts = serializers.SerializerMethodField()
    class Meta:
        model  = Question
        fields = ['id', 'question_text', 'image', 'multiple_answers', 'options', "correct_option_ids", "correct_option_texts",]

    def get_correct_option_ids(self, obj):
        # uses prefetch below so it won't re-hit DB
        return [opt.id for opt in obj.options.all() if opt.is_correct]

    def get_correct_option_texts(self, obj):
        return [opt.text for opt in obj.options.all() if opt.is_correct]


class QuestionForTestSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)
    correct_option_ids = serializers.SerializerMethodField()
    correct_option_texts = serializers.SerializerMethodField()

    class Meta:
        model  = Question
        fields = [
            "id",
            "question_text",
            "image",
            "multiple_answers",
            "options",
            "correct_option_ids",
            "correct_option_texts",
        ]

    def get_correct_option_ids(self, obj):
        return [opt.id for opt in obj.options.all() if opt.is_correct]

    def get_correct_option_texts(self, obj):
        return [opt.text for opt in obj.options.all() if opt.is_correct]


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
