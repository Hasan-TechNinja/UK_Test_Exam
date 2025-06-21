# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, UserEvaluation

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Profile)
def create_user_evaluation(sender, instance, created, **kwargs):
    """
    If a new Profile was just created, make its first UserEvaluation.
    """
    if created:
        UserEvaluation.objects.create(
            user=instance,             
            PracticeCompleted="0",      
            QuestionAnswered="0",
            CorrectAnswered="0",
            WrongAnswered="0",    
        )
