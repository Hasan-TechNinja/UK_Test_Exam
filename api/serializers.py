from rest_framework import serializers
from main.models import Unit, Lesson, Question
from django.contrib.auth.models import User

class UnitModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        # fields = "__all__"
        exclude = ['created']

class LessonSerializers(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        exclude = ['user', 'created']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
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
