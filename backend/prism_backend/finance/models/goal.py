from django.db import models
from django.conf import settings
from decimal import Decimal


class Goal(models.Model):
    """
    Financial goals for users to track savings targets.
    Can be linked to specific accounts or be general savings goals.
    """
    GOAL_TYPES = [
        ('savings', 'Savings Goal'),
        ('debt', 'Debt Payoff'),
        ('investment', 'Investment Target'),
        ('purchase', 'Purchase Goal'),
        ('emergency', 'Emergency Fund'),
        ('other', 'Other'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goals'
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES, default='savings')
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    target_date = models.DateField(null=True, blank=True)

    # Optional account association
    linked_account = models.ForeignKey(
        'Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='goals'
    )

    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.current_amount}/{self.target_amount}"

    @property
    def remaining_amount(self):
        """Calculate remaining amount to reach goal"""
        return max(Decimal('0.00'), self.target_amount - self.current_amount)

    @property
    def progress_percentage(self):
        """Calculate progress as percentage"""
        if self.target_amount == 0:
            return 0
        return min(100, (self.current_amount / self.target_amount) * 100)

    @property
    def is_goal_reached(self):
        """Check if goal has been reached"""
        return self.current_amount >= self.target_amount

    def update_progress(self, amount):
        """Update current amount and check if goal is completed"""
        self.current_amount = amount

        if self.is_goal_reached and not self.is_completed:
            self.is_completed = True
            from django.utils import timezone
            self.completed_at = timezone.now()
        elif not self.is_goal_reached and self.is_completed:
            # Goal was completed but current amount dropped below target
            self.is_completed = False
            self.completed_at = None

        self.save()

    def save(self, *args, **kwargs):
        # Ensure owner consistency
        if self.linked_account and self.linked_account.owner != self.owner:
            raise ValueError("Linked account must belong to the same owner")

        # Auto-complete goal if target is reached
        if self.is_goal_reached and not self.is_completed:
            self.is_completed = True
            if not self.completed_at:
                from django.utils import timezone
                self.completed_at = timezone.now()

        super().save(*args, **kwargs)