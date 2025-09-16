from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ots_app.models import Subject, Question

User = get_user_model()


class Command(BaseCommand):
    help = 'Create demo data for the OTS application'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(f'Created admin user: {admin.username}')
        
        # Create student user
        if not User.objects.filter(username='student').exists():
            student = User.objects.create_user(
                username='student',
                email='student@example.com',
                password='student123',
                first_name='John',
                last_name='Doe',
                role='student'
            )
            self.stdout.write(f'Created student user: {student.username}')
        
        # Create subjects
        subjects_data = [
            {'name': 'Mathematics', 'description': 'Basic mathematics questions'},
            {'name': 'Science', 'description': 'General science questions'},
            {'name': 'English', 'description': 'English language questions'},
        ]
        
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                name=subject_data['name'],
                defaults={'description': subject_data['description']}
            )
            if created:
                self.stdout.write(f'Created subject: {subject.name}')
        
        # Create sample questions for Mathematics
        math_subject = Subject.objects.get(name='Mathematics')
        math_questions = [
            {
                'question': 'What is 2 + 2?',
                'option_a': '3', 'option_b': '4', 'option_c': '5', 'option_d': '6',
                'correct_answer': 'B', 'explanation': '2 + 2 equals 4'
            },
            {
                'question': 'What is 5 × 3?',
                'option_a': '15', 'option_b': '12', 'option_c': '18', 'option_d': '20',
                'correct_answer': 'A', 'explanation': '5 multiplied by 3 equals 15'
            },
        ]
        
        for question_data in math_questions:
            question, created = Question.objects.get_or_create(
                subject=math_subject,
                question=question_data['question'],
                defaults=question_data
            )
            if created:
                self.stdout.write(f'Created question: {question.question[:30]}...')
        
        self.stdout.write(self.style.SUCCESS('Demo data created successfully!'))
        self.stdout.write('Demo accounts:')
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Student: student / student123')
