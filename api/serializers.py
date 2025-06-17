from rest_framework import serializers
from main.models import Chapter, Lesson, Question, Profile, GuidesSupport, UserEvaluation, HomePage, LessonContent, GuideSupportContent, PracticeOption, PracticeQuestion
from subscriptions.models import SubscriptionPlan, UserSubscription
from django.contrib.auth.models import User

class ChapterModelSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()
    class Meta:
        model = Chapter
        # fields = "__all__"
        exclude = ['created']

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def get_title(self, obj):
        return f"Chapter {obj.id}"

    def get_lessons(self, obj):
        lesson_qs = obj.lesson_set.all().order_by('id')
        return [f"{i+1}" for i, _ in enumerate(lesson_qs)]

    def create(self, validated_data):
        return super().create(validated_data)
    

class LessonModelSerializers(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Lesson
        exclude = ['created']

    def create(self, validated_data):
    
        return super().create(validated_data)

    

class QuestionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ProfileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ["user", "created_at"]


class GuidesSupportModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuidesSupport
        exclude = ['status', 'created']


class GuideSupportContentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideSupportContent
        fields = ['id', 'image', 'description', 'video']




class UserEvaluationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEvaluation
        exclude = ['user']



class HomePageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = ['title', 'description', 'image']




class LessonContentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonContent
        fields = "__all__"



class PracticeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PracticeOption
        fields = ['text']

class PracticeQuestionSerializer(serializers.ModelSerializer):
    options = PracticeOptionSerializer(many=True, read_only=True)
    class Meta:
        model  = PracticeQuestion
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

