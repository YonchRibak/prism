from django.db import models
from django.conf import settings
from decimal import Decimal


class Transaction(models.Model):
    """
    Individual financial transactions.
    Positive amounts = income, negative amounts = expenses.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    account = models.ForeignKey(
        'Account',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField()
    notes = models.TextField(blank=True)

    # For transfers between accounts
    transfer_to = models.ForeignKey(
        'Account',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='transfer_in'
    )

    # Recurring transaction support
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ],
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['owner', 'date']),
            models.Index(fields=['owner', 'account']),
            models.Index(fields=['owner', 'category']),
        ]

    def __str__(self):
        return f"{self.date}: {self.description} ({self.amount})"

    @property
    def is_expense(self):
        return self.amount < 0

    @property
    def is_income(self):
        return self.amount > 0

    @property
    def is_transfer(self):
        return self.transfer_to is not None

    def save(self, *args, **kwargs):
        # Ensure owner consistency
        if self.account and self.account.owner != self.owner:
            raise ValueError("Transaction account must belong to the same owner")
        if self.category and self.category.owner != self.owner:
            raise ValueError("Transaction category must belong to the same owner")
        if self.transfer_to and self.transfer_to.owner != self.owner:
            raise ValueError("Transfer account must belong to the same owner")

        super().save(*args, **kwargs)