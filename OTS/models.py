from django.db import models

class Candidate(models.Model):
    username = models.CharField(primary_key=True, max_length=20)
    password = models.CharField(null=False, max_length=20)
    name = models.CharField(null=False, max_length=30)
    test_attempted = models.IntegerField(default=0)
    points = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.name} ({self.username})"


class Question(models.Model):
    qid = models.BigAutoField(primary_key=True, auto_created=True)
    que = models.TextField()
    a = models.CharField(max_length=255)
    b = models.CharField(max_length=255)
    c = models.CharField(max_length=255)
    d = models.CharField(max_length=255)
    ans = models.CharField(max_length=2)  # expected values: 'A'|'B'|'C'|'D'

    def __str__(self):
        return f"Q{self.qid}: {self.que[:50]}..."


class Result(models.Model):
    resultid = models.BigAutoField(primary_key=True, auto_created=True)
    username = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    time = models.TimeField(auto_now=True)
    attempt = models.IntegerField()
    right = models.IntegerField()
    wrong = models.IntegerField()
    points = models.FloatField()
    # New: per-question details used for review and chatbot
    # Each item: { qid, question, options: {A,B,C,D}, correct, user, is_correct }
    details = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.username.name} - {self.date} - {self.points} points"

    class Meta:
        ordering = ['-resultid']


class TestConfig(models.Model):
    # Admin time rules by test length
    minutes_short = models.PositiveIntegerField(
        default=3,
        help_text="Time limit (minutes) when number of questions <= 5"
    )
    minutes_medium = models.PositiveIntegerField(
        default=10,
        help_text="Time limit (minutes) when 6-10 questions"
    )
    minutes_long = models.PositiveIntegerField(
        default=20,
        help_text="Time limit (minutes) when > 10 questions"
    )
    fallback_minutes_per_question = models.PositiveIntegerField(
        default=1,
        help_text="Fallback minutes per question if rules are not desired"
    )
    show_leave_warning = models.BooleanField(
        default=True,
        help_text="Warn users when leaving the page during a test"
    )

    def __str__(self):
        return f"Test Time Rules (short={self.minutes_short}m, medium={self.minutes_medium}m, long={self.minutes_long}m)"
