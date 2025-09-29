from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class SubscriptionPlan(models.Model):
    """
    Defines the available subscription plans (e.g., 1 Week, 1 Month, Lifetime).
    """
    PLAN_CHOICES = [
        ('1_week', '1 Week Access'),
        ('1_month', '1 Month Access'),
        ('lifetime', 'Lifetime Access'),
    ]
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True, help_text="Unique name for the subscription plan (e.g., '1_week', 'lifetime')")
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Price of the subscription plan.")
    duration_days = models.IntegerField(null=True, blank=True, help_text="Duration of the plan in days. Null for lifetime access.")
    features = models.TextField(blank=True, help_text="Comma-separated list of features included in this plan.")

    class Meta:
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"
        ordering = ['price'] # Order plans by price by default

    def __str__(self):
        return f"{self.get_name_display()} - £{self.price}"

class UserSubscription(models.Model):
    """
    Tracks a user's active subscription to a plan.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, help_text="The user associated with this subscription.")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, help_text="The subscription plan the user is subscribed to.")
    start_date = models.DateTimeField(auto_now_add=True, help_text="The date and time the subscription started.")
    end_date = models.DateTimeField(null=True, blank=True, help_text="The date and time the subscription ends. Null for lifetime.")
    is_active = models.BooleanField(default=False, help_text="Indicates if the subscription is currently active.")
    last_renewed = models.DateTimeField(null=True, blank=True, help_text="Date of last successful renewal (for recurring plans).")
    device_id = models.CharField(max_length=255, blank=True, help_text="Information about the device used for subscription (if applicable).")

    class Meta:
        verbose_name = "User Subscription"
        verbose_name_plural = "User Subscriptions"

    def __str__(self):
        return f"{self.user.username}'s {self.plan.name if self.plan else 'Inactive'} Subscription"

    def save(self, *args, **kwargs):
        # Automatically calculate end_date for non-lifetime plans on save
        if self.plan and self.plan.duration_days and not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_currently_active(self):
        """
        Checks if the subscription is active based on end_date (if applicable).
        """
        if not self.is_active:
            return False
        if self.plan and self.plan.name == 'lifetime':
            return True
        if self.end_date and timezone.now() < self.end_date:
            return True
        return False