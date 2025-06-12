from rest_framework import serializers
from main.models import Chapter, Lesson, Question, Profile, GuidesSupport, UserEvaluation, HomePage, LessonContent, GuideSupportList
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



class UserEvaluationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEvaluation
        exclude = ['user']



class HomePageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model =HomePage
        fields = "__all__"




class LessonContentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonContent
        fields = "__all__"




class GuideSupportListModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideSupportList
        fields = "__all__"