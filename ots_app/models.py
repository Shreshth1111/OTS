from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import json


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    question = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    explanation = models.TextField(blank=True)

    def __str__(self):
        return f"{self.subject.name} - {self.question[:50]}..."


class Test(models.Model):
    STATUS_CHOICES = [
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    questions = models.JSONField(default=list)  # Store question data as JSON
    answers = models.JSONField(default=dict)  # Store answers as JSON
    total_questions = models.IntegerField()
    score = models.IntegerField(default=0)
    time_limit = models.IntegerField()  # in minutes
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in-progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} - {self.status}"

    @property
    def is_expired(self):
        if self.status == 'completed':
            return False
        time_elapsed = timezone.now() - self.start_time
        return time_elapsed.total_seconds() > (self.time_limit * 60)


class TestResult(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+'),
        ('A', 'A'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('C+', 'C+'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    ]
    
    test = models.OneToOneField(Test, on_delete=models.CASCADE, related_name='result')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    wrong_answers = models.IntegerField()
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES)
    percentage = models.FloatField()
    time_taken = models.IntegerField()  # in minutes
    question_results = models.JSONField(default=list)  # Detailed question-wise results
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} - {self.grade}"

    @staticmethod
    def calculate_grade(percentage):
        if percentage >= 95:
            return 'A+'
        elif percentage >= 90:
            return 'A'
        elif percentage >= 85:
            return 'B+'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 75:
            return 'C+'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'

    class Meta:
        ordering = ['-created_at']
