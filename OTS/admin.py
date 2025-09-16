from django.contrib import admin
from .models import Candidate, Question, Result, TestConfig

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'test_attempted', 'points']
    search_fields = ['username', 'name']
    list_filter = ['test_attempted']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['qid', 'que', 'ans']
    search_fields = ['que']
    list_filter = ['ans']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['resultid', 'username', 'date', 'time', 'points', 'right', 'wrong']
    list_filter = ['date', 'points']
    search_fields = ['username__name', 'username__username']

@admin.register(TestConfig)
class TestConfigAdmin(admin.ModelAdmin):
    list_display = ["minutes_short", "minutes_medium", "minutes_long", "fallback_minutes_per_question", "show_leave_warning"]
    fieldsets = (
        ("Per-length rules", {
            "fields": ("minutes_short", "minutes_medium", "minutes_long")
        }),
        ("Fallbacks and options", {
            "fields": ("fallback_minutes_per_question", "show_leave_warning")
        })
    )
