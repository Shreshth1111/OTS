from django.core.management.base import BaseCommand
from OTS.models import Candidate, Question

class Command(BaseCommand):
    help = 'Create sample data for the OTS application'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample candidates
        if not Candidate.objects.filter(username='demo').exists():
            candidate = Candidate.objects.create(
                username='demo',
                password='demo123',
                name='Demo User'
            )
            self.stdout.write(f'Created candidate: {candidate.name}')
        
        # Create sample questions
        sample_questions = [
            {
                'que': 'What is the capital of France?',
                'a': 'London',
                'b': 'Berlin',
                'c': 'Paris',
                'd': 'Madrid',
                'ans': 'C'
            },
            {
                'que': 'Which planet is known as the Red Planet?',
                'a': 'Venus',
                'b': 'Mars',
                'c': 'Jupiter',
                'd': 'Saturn',
                'ans': 'B'
            },
            {
                'que': 'What is 2 + 2?',
                'a': '3',
                'b': '4',
                'c': '5',
                'd': '6',
                'ans': 'B'
            },
            {
                'que': 'Who wrote "Romeo and Juliet"?',
                'a': 'Charles Dickens',
                'b': 'William Shakespeare',
                'c': 'Jane Austen',
                'd': 'Mark Twain',
                'ans': 'B'
            },
            {
                'que': 'What is the largest ocean on Earth?',
                'a': 'Atlantic Ocean',
                'b': 'Indian Ocean',
                'c': 'Arctic Ocean',
                'd': 'Pacific Ocean',
                'ans': 'D'
            },
            {
                'que': 'Which gas do plants absorb from the atmosphere?',
                'a': 'Oxygen',
                'b': 'Nitrogen',
                'c': 'Carbon Dioxide',
                'd': 'Hydrogen',
                'ans': 'C'
            },
            {
                'que': 'What is the square root of 16?',
                'a': '2',
                'b': '3',
                'c': '4',
                'd': '5',
                'ans': 'C'
            },
            {
                'que': 'Which country is known as the Land of the Rising Sun?',
                'a': 'China',
                'b': 'Japan',
                'c': 'Korea',
                'd': 'Thailand',
                'ans': 'B'
            },
            {
                'que': 'What is the chemical symbol for water?',
                'a': 'H2O',
                'b': 'CO2',
                'c': 'NaCl',
                'd': 'O2',
                'ans': 'A'
            },
            {
                'que': 'How many continents are there?',
                'a': '5',
                'b': '6',
                'c': '7',
                'd': '8',
                'ans': 'C'
            },
            {
                'que': 'What is the fastest land animal?',
                'a': 'Lion',
                'b': 'Cheetah',
                'c': 'Horse',
                'd': 'Leopard',
                'ans': 'B'
            },
            {
                'que': 'Which element has the chemical symbol "Au"?',
                'a': 'Silver',
                'b': 'Gold',
                'c': 'Aluminum',
                'd': 'Copper',
                'ans': 'B'
            },
            {
                'que': 'What is 10 × 5?',
                'a': '45',
                'b': '50',
                'c': '55',
                'd': '60',
                'ans': 'B'
            },
            {
                'que': 'Which is the smallest prime number?',
                'a': '0',
                'b': '1',
                'c': '2',
                'd': '3',
                'ans': 'C'
            },
            {
                'que': 'What is the currency of the United Kingdom?',
                'a': 'Euro',
                'b': 'Dollar',
                'c': 'Pound',
                'd': 'Yen',
                'ans': 'C'
            },
            {
                'que': 'Which organ in the human body produces insulin?',
                'a': 'Liver',
                'b': 'Kidney',
                'c': 'Heart',
                'd': 'Pancreas',
                'ans': 'D'
            },
            {
                'que': 'What is the boiling point of water at sea level?',
                'a': '90°C',
                'b': '100°C',
                'c': '110°C',
                'd': '120°C',
                'ans': 'B'
            },
            {
                'que': 'Which programming language is known for its use in web development?',
                'a': 'C++',
                'b': 'Java',
                'c': 'JavaScript',
                'd': 'Python',
                'ans': 'C'
            },
            {
                'que': 'What is the largest mammal in the world?',
                'a': 'Elephant',
                'b': 'Blue Whale',
                'c': 'Giraffe',
                'd': 'Hippopotamus',
                'ans': 'B'
            },
            {
                'que': 'Which year did World War II end?',
                'a': '1944',
                'b': '1945',
                'c': '1946',
                'd': '1947',
                'ans': 'B'
            }
        ]
        
        for question_data in sample_questions:
            question, created = Question.objects.get_or_create(
                que=question_data['que'],
                defaults=question_data
            )
            if created:
                self.stdout.write(f'Created question: {question.que[:50]}...')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write('Demo account: demo / demo123')
