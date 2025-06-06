from rest_framework import serializers
from main.models import Chapter, Lesson, Question, Profile, GuidesSupport
from django.contrib.auth.models import User

class ChapterModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        # fields = "__all__"
        exclude = ['created']

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def create(self, validated_data):
        # You can remove this if you're using HiddenField
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