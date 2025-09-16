from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Subject, Question, Test, TestResult


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                    return data
                else:
                    raise serializers.ValidationError('User account is disabled.')
            else:
                raise serializers.ValidationError('Invalid username or password.')
        else:
            raise serializers.ValidationError('Must include username and password.')


class SubjectSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'question_count', 'created_at']
    
    def get_question_count(self, obj):
        return obj.questions.count()


class QuestionSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'subject', 'subject_name', 'question', 'option_a', 'option_b', 
            'option_c', 'option_d', 'correct_answer', 'explanation', 'difficulty'
        ]


class TestSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    
    class Meta:
        model = Test
        fields = [
            'id', 'student', 'student_name', 'subject', 'subject_name', 
            'questions', 'answers', 'total_questions', 'score', 'time_limit',
            'start_time', 'end_time', 'status', 'created_at'
        ]


class TestResultSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    test_date = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = TestResult
        fields = [
            'id', 'test', 'student', 'student_name', 'subject', 'subject_name',
            'score', 'total_questions', 'correct_answers', 'wrong_answers',
            'grade', 'percentage', 'time_taken', 'question_results', 'test_date'
        ]
