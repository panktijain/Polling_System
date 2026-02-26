from django.conf import settings
from django.db import models



# Predefined poll categories
class Poll(models.Model):
    # Predefined poll categories
    CATEGORY_CHOICES = [
        ("technology", "Technology"),
        ("education", "Education"),
        ("entertainment", "Entertainment"),
        ("college_life", "College Life"),
        ("sports", "Sports"),
    ]

    question = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=False)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="technology",
        help_text="Select a category for this poll."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='polls',
    )

    def __str__(self):
        # Return poll question for admin and shell display
        return self.question

    def total_votes(self):
        # Aggregate total votes for all options
        return self.options.aggregate(total=models.Sum('vote_count'))['total'] or 0

    def __str__(self):
        return self.question

    def total_votes(self):
        return self.options.aggregate(total=models.Sum('vote_count'))['total'] or 0


class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255, blank=False)
    
    vote_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.text
    #calculate percentage of votes for this option
    def percentage(self, total_votes): 
        if total_votes == 0:
            return 0
        return round((self.vote_count / total_votes) * 100, 1)


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='votes')
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poll')

    def __str__(self):
        return f"{self.user.username} -> {self.poll.question}"
