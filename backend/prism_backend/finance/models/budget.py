from django.db import models
from django.conf import settings
from decimal import Decimal


class Budget(models.Model):
    """
    Budget tracking for categories over specific time periods.
    Helps users monitor spending against planned amounts.
    """
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='monthly')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        unique_together = ['owner', 'category', 'start_date', 'end_date']

    def __str__(self):
        return f"{self.name} - {self.category.name} ({self.period})"

    @property
    def spent_amount(self):
        """Calculate total spent in this budget's category and time period"""
        from .transaction import Transaction
        transactions = Transaction.objects.filter(
            owner=self.owner,
            category=self.category,
            date__gte=self.start_date,
            date__lte=self.end_date,
            amount__lt=0  # Only expenses (negative amounts)
        )
        return abs(sum(t.amount for t in transactions) or Decimal('0.00'))

    @property
    def remaining_amount(self):
        """Calculate remaining budget amount"""
        return max(Decimal('0.00'), self.amount - self.spent_amount)

    @property
    def percentage_used(self):
        """Calculate percentage of budget used"""
        if self.amount == 0:
            return 0
        return min(100, (self.spent_amount / self.amount) * 100)

    @property
    def is_over_budget(self):
        """Check if spending exceeds budget"""
        return self.spent_amount > self.amount

    def save(self, *args, **kwargs):
        # Ensure owner consistency
        if self.category and self.category.owner != self.owner:
            raise ValueError("Budget category must belong to the same owner")

        # Validate date range
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")

        super().save(*args, **kwargs)