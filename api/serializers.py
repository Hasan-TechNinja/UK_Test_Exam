from rest_framework import serializers
from main.models import Chapter, Glossary, GuidesSupportGlossary, Lesson, Profile, GuidesSupport, QuestionGlossary, UserEvaluation, HomePage, LessonContent, GuideSupportContent, QuestionOption, Question, MockTestSession, MockTestAnswer, FreeMockTestSession, FreeMockTestAnswer
from subscriptions.models import SubscriptionPlan, UserSubscription
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

from main.models import EmailVerification
from django.core.mail import send_mail
import random
import json
from django.utils.text import slugify
from django.db import transaction




class ChapterModelSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = ['id', 'name', 'description', 'lessons']

    def get_lessons(self, obj):
        lesson_qs = obj.lesson_set.all().order_by('id')
        return [f"{i+1}" for i, _ in enumerate(lesson_qs)]


class LessonModelSerializers(serializers.ModelSerializer):
    # Read-only nested object for responses
    chapter = ChapterModelSerializer(read_only=True)
    # Write-only field for requests (accepts the id)
    chapter_id = serializers.PrimaryKeyRelatedField(
        source="chapter",
        queryset=Chapter.objects.all(),
        write_only=True
    )

    class Meta:
        model = Lesson
        # include both; created excluded as you had
        fields = ("id", "name", "title", "chapter", "chapter_id")


class GlossaryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Glossary
        fields = ['id', 'title', 'description']


class LessonContentModelSerializer(serializers.ModelSerializer):
    chapter_name = serializers.CharField(source='lesson.chapter.name', read_only=True)
    glossaries = GlossaryModelSerializer(many=True, read_only=True)

    class Meta:
        model = LessonContent
        fields = ['id', 'chapter_name', 'lesson', 'image', 'description', 'video', 'glossaries']



class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="This email is already in use.")]
    )
    password = serializers.CharField(write_only=True, validators=[validate_password])

    # NEW: accept phone during registration (write-only; not a User field)
    phone = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=50
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'phone']  # include phone here

    @transaction.atomic
    def create(self, validated_data):
        phone = validated_data.pop('phone', None)  # get phone from payload
        email = validated_data['email']

        # create unique username from email
        username_base = slugify(email.split('@')[0]) or "user"
        username = username_base
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

        # ensure a Profile exists and set the phone
        profile, _ = Profile.objects.get_or_create(user=user)
        if phone:
            profile.phone = phone
            profile.save(update_fields=["phone"])

        # send verification code
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


class GuideSupportGlossarySerializer(serializers.ModelSerializer):
    class Meta:
        model = GuidesSupportGlossary
        fields = ['id', 'guide', 'title', 'description']


class GuideSupportContentModelSerializer(serializers.ModelSerializer):
    glossary_list = serializers.SerializerMethodField()

    class Meta:
        model = GuideSupportContent
        fields = ['id', 'image', 'description', 'video', 'created', 'glossary_list']

    def get_glossary_list(self, obj):
        glossaries = obj.glossaries.all()
        return [
            {
                "id": g.id,
                "title": g.title,
                "description": g.description,
            }
            for g in glossaries
        ]



class UserEvaluationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEvaluation
        fields = "__all__"
        # exclude = ['user']



class HomePageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = ['title', 'description', 'image']



    
# class LessonContentModelSerializer(serializers.ModelSerializer):
#     chapter_name = serializers.CharField(source='lesson.chapter.name', read_only=True)

#     class Meta:
#         model = LessonContent
#         fields = ['id', 'chapter_name', 'lesson', 'image', 'description', 'video', 'glossary']


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
        fields = ['id', 'text', 'is_correct']

class QuestionGlossarySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionGlossary
        fields = ["id", "title", "definition"]


class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)
    correct_option_ids = serializers.SerializerMethodField()
    correct_option_texts = serializers.SerializerMethodField()
    glossaries = QuestionGlossarySerializer(source="glossary", many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "question_text",
            "image",
            "multiple_answers",
            "options",
            "correct_option_ids",
            "correct_option_texts",
            "explanation",
            "glossaries",
        ]

    def get_correct_option_ids(self, obj):
        # already prefetched in view
        return [opt.id for opt in obj.options.all() if opt.is_correct]

    def get_correct_option_texts(self, obj):
        return [opt.text for opt in obj.options.all() if opt.is_correct]
    
    

'''
class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)
    correct_option_ids = serializers.SerializerMethodField()
    correct_option_texts = serializers.SerializerMethodField()
    glossaries = serializers.SerializerMethodField()
    class Meta:
        model  = Question
        fields = ['id', 'question_text', 'image', 'multiple_answers', 'options', "correct_option_ids", "correct_option_texts", "explanation", "glossaries"]

    def get_correct_option_ids(self, obj):
        # uses prefetch below so it won't re-hit DB
        return [opt.id for opt in obj.options.all() if opt.is_correct]

    def get_correct_option_texts(self, obj):
        return [opt.text for opt in obj.options.all() if opt.is_correct]
    
    def get_glossaries(self, obj):
        glossaries = Glossary.objects.filter(
            lesson_content__lesson__chapter=obj.chapter
        ).distinct()
        return GlossaryModelSerializer(glossaries, many=True).data
'''

class QuestionForTestSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)
    correct_option_ids = serializers.SerializerMethodField()
    correct_option_texts = serializers.SerializerMethodField()
    glossaries = QuestionGlossarySerializer(source="glossary", many=True, read_only=True)

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
            "explanation", 
            "glossaries",
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


class CSVUploadSerializer(serializers.Serializer):
    csv_file = serializers.FileField()