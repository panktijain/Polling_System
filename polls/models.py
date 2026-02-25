from django.conf import settings
from django.db import models


class Poll(models.Model):
    question = models.CharField(max_length=255, blank=False)
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
        return self.question

    def total_votes(self):
        return self.options.aggregate(total=models.Sum('vote_count'))['total'] or 0


class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255, blank=False)
    vote_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.text

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
