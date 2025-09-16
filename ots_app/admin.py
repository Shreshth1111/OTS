from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Subject, Question


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role']
    list_filter = ['role']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question', 'subject', 'correct_answer']
    list_filter = ['subject']
