from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ots_app.models import Subject, Question

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
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
            {'name': 'History', 'description': 'World history questions'},
        ]
        
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                name=subject_data['name'],
                defaults={'description': subject_data['description']}
            )
            if created:
                self.stdout.write(f'Created subject: {subject.name}')
        
        # Create sample questions
        math_subject = Subject.objects.get(name='Mathematics')
        science_subject = Subject.objects.get(name='Science')
        english_subject = Subject.objects.get(name='English')
        history_subject = Subject.objects.get(name='History')
        
        # Mathematics questions
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
            {
                'question': 'What is the square root of 16?',
                'option_a': '2', 'option_b': '3', 'option_c': '4', 'option_d': '5',
                'correct_answer': 'C', 'explanation': 'The square root of 16 is 4'
            },
            {
                'question': 'What is 10 - 7?',
                'option_a': '2', 'option_b': '3', 'option_c': '4', 'option_d': '5',
                'correct_answer': 'B', 'explanation': '10 minus 7 equals 3'
            },
            {
                'question': 'What is 8 ÷ 2?',
                'option_a': '3', 'option_b': '4', 'option_c': '5', 'option_d': '6',
                'correct_answer': 'B', 'explanation': '8 divided by 2 equals 4'
            },
        ]
        
        # Science questions
        science_questions = [
            {
                'question': 'What is the chemical symbol for water?',
                'option_a': 'H2O', 'option_b': 'CO2', 'option_c': 'NaCl', 'option_d': 'O2',
                'correct_answer': 'A', 'explanation': 'Water is H2O - two hydrogen atoms and one oxygen atom'
            },
            {
                'question': 'How many planets are in our solar system?',
                'option_a': '7', 'option_b': '8', 'option_c': '9', 'option_d': '10',
                'correct_answer': 'B', 'explanation': 'There are 8 planets in our solar system'
            },
            {
                'question': 'What gas do plants absorb from the atmosphere?',
                'option_a': 'Oxygen', 'option_b': 'Nitrogen', 'option_c': 'Carbon Dioxide', 'option_d': 'Hydrogen',
                'correct_answer': 'C', 'explanation': 'Plants absorb carbon dioxide for photosynthesis'
            },
            {
                'question': 'What is the hardest natural substance?',
                'option_a': 'Gold', 'option_b': 'Iron', 'option_c': 'Diamond', 'option_d': 'Silver',
                'correct_answer': 'C', 'explanation': 'Diamond is the hardest natural substance'
            },
            {
                'question': 'What is the speed of light?',
                'option_a': '300,000 km/s', 'option_b': '150,000 km/s', 'option_c': '450,000 km/s', 'option_d': '600,000 km/s',
                'correct_answer': 'A', 'explanation': 'The speed of light is approximately 300,000 kilometers per second'
            },
        ]
        
        # Create questions for each subject
        for question_data in math_questions:
            question, created = Question.objects.get_or_create(
                subject=math_subject,
                question=question_data['question'],
                defaults=question_data
            )
            if created:
                self.stdout.write(f'Created math question: {question.question[:30]}...')
        
        for question_data in science_questions:
            question, created = Question.objects.get_or_create(
                subject=science_subject,
                question=question_data['question'],
                defaults=question_data
            )
            if created:
                self.stdout.write(f'Created science question: {question.question[:30]}...')
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        self.stdout.write('Demo accounts:')
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Student: student / student123')
