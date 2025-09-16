from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.middleware.csrf import get_token
from django.contrib import messages
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
import json
import random

from .models import User, Subject, Question, Test, TestResult
from .serializers import (
    UserSerializer, LoginSerializer, SubjectSerializer, 
    QuestionSerializer, TestSerializer, TestResultSerializer
)

# Template Views
def index(request):
    """Main index page - redirect based on authentication"""
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('dashboard')
    return redirect('login_page')

def login_page(request):
    """Login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'auth/login.html')

def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('login_page')

@login_required
def dashboard(request):
    """Student dashboard"""
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    
    context = {
        'user': request.user,
        'subjects': Subject.objects.all()
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def admin_dashboard(request):
    """Admin dashboard"""
    if request.user.role != 'admin':
        return redirect('dashboard')
    
    context = {
        'user': request.user,
        'total_students': User.objects.filter(role='student').count(),
        'total_subjects': Subject.objects.count(),
        'total_questions': Question.objects.count(),
    }
    return render(request, 'admin/index.html', context)

@login_required
def tests_page(request):
    """Tests page"""
    subjects = Subject.objects.all()
    return render(request, 'tests/index.html', {'subjects': subjects})

@login_required
def test_page(request, test_id):
    """Individual test page"""
    return render(request, 'tests/test.html', {'test_id': test_id})

@login_required
def results_page(request):
    """Results page"""
    return render(request, 'results/index.html')

@login_required
def result_detail_page(request, result_id):
    """Result detail page"""
    return render(request, 'results/detail.html', {'result_id': result_id})

@login_required
def admin_page(request):
    """Admin page"""
    if request.user.role != 'admin':
        return render(request, 'errors/403.html')
    return render(request, 'admin/index.html')

# API Views
class LoginView(APIView):
    """Login API view"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                'success': True,
                'user': UserSerializer(user).data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    """Register API view"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({
                'success': True,
                'user': UserSerializer(user).data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """Logout API view"""
    
    def post(self, request):
        logout(request)
        return Response({'success': True})

class CurrentUserView(APIView):
    """Get current user"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

class SubjectListView(generics.ListCreateAPIView):
    """Subject list and create view"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

class QuestionListView(generics.ListCreateAPIView):
    """Question list and create view"""
    serializer_class = QuestionSerializer
    
    def get_queryset(self):
        queryset = Question.objects.all()
        subject_id = self.request.query_params.get('subject_id')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        return queryset

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_test(request):
    """Create a new test"""
    try:
        subject_id = request.data.get('subject_id')
        question_count = request.data.get('question_count', 15)
        
        # Get random questions
        questions = list(Question.objects.filter(subject_id=subject_id).order_by('?')[:question_count])
        
        if not questions:
            return Response({
                'error': 'No questions available for this subject'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Serialize questions
        questions_data = QuestionSerializer(questions, many=True).data
        
        # Determine time limit
        time_limit = 25 if question_count == 15 else 45
        
        # Create test
        test = Test.objects.create(
            student=request.user,
            subject_id=subject_id,
            questions=questions_data,
            total_questions=len(questions),
            time_limit=time_limit,
            start_time=timezone.now(),
            status='in-progress'
        )
        
        return Response({
            'success': True,
            'test_id': test.id
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_test(request, test_id):
    """Get test details"""
    try:
        test = get_object_or_404(Test, id=test_id, student=request.user)
        serializer = TestSerializer(test)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_test(request, test_id):
    """Submit test answers"""
    try:
        test = get_object_or_404(Test, id=test_id, student=request.user)
        answers = request.data.get('answers', {})
        
        # Calculate results
        correct_answers = 0
        question_results = []
        
        for question_data in test.questions:
            question_id = str(question_data['id'])
            user_answer = answers.get(question_id, '')
            correct_answer = question_data['correct_answer']
            is_correct = user_answer.lower().strip() == correct_answer.lower().strip()
            
            if is_correct:
                correct_answers += 1
            
            question_results.append({
                'question_id': question_id,
                'question': question_data['question'],
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question_data.get('explanation', '')
            })
        
        # Calculate score and grade
        score = correct_answers
        percentage = round((correct_answers / test.total_questions) * 100)
        grade = TestResult.calculate_grade(percentage)
        
        # Calculate time taken
        time_taken = min(test.time_limit, 
                        int((timezone.now() - test.start_time).total_seconds() / 60))
        
        # Update test
        test.answers = answers
        test.score = score
        test.status = 'completed'
        test.end_time = timezone.now()
        test.save()
        
        # Create test result
        test_result = TestResult.objects.create(
            test=test,
            student=request.user,
            subject=test.subject,
            score=score,
            total_questions=test.total_questions,
            correct_answers=correct_answers,
            wrong_answers=test.total_questions - correct_answers,
            grade=grade,
            percentage=percentage,
            time_taken=time_taken,
            question_results=question_results
        )
        
        return Response({
            'success': True,
            'result_id': test_result.id,
            'score': score,
            'percentage': percentage,
            'grade': grade,
            'correct_answers': correct_answers,
            'total_questions': test.total_questions
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_student_stats(request, student_id):
    """Get student statistics"""
    try:
        if request.user.role != 'admin' and str(request.user.id) != student_id:
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        results = TestResult.objects.filter(student_id=student_id)
        
        stats = {
            'total_tests': results.count(),
            'completed_tests': results.count(),
            'average_score': round(sum(r.percentage for r in results) / len(results)) if results else 0,
            'best_score': max(r.percentage for r in results) if results else 0
        }
        
        return Response(stats)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_student_results(request, student_id):
    """Get student test results"""
    try:
        if request.user.role != 'admin' and str(request.user.id) != student_id:
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        results = TestResult.objects.filter(student_id=student_id)
        serializer = TestResultSerializer(results, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_result_detail(request, result_id):
    """Get detailed test result"""
    try:
        if request.user.role == 'admin':
            result = get_object_or_404(TestResult, id=result_id)
        else:
            result = get_object_or_404(TestResult, id=result_id, student=request.user)
        
        serializer = TestResultSerializer(result)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Admin Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_stats(request):
    """Get admin dashboard statistics"""
    if request.user.role != 'admin':
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        stats = {
            'total_students': User.objects.filter(role='student').count(),
            'total_subjects': Subject.objects.count(),
            'total_questions': Question.objects.count(),
            'total_tests': TestResult.objects.count()
        }
        return Response(stats)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def admin_students(request):
    """Admin students management"""
    if request.user.role != 'admin':
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        students = User.objects.filter(role='student')
        serializer = UserSerializer(students, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(role='student')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def admin_student_detail(request, student_id):
    """Admin student detail management"""
    if request.user.role != 'admin':
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    student = get_object_or_404(User, id=student_id, role='student')
    
    if request.method == 'PUT':
        serializer = UserSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        student.delete()
        return Response({'success': True})

# Chatbot API
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def chatbot(request):
    """Simple rule-based chatbot for helping students"""
    try:
        message = request.data.get('message', '').lower()
        context = request.data.get('context', {})
        
        # Simple responses based on keywords
        if 'hello' in message or 'hi' in message:
            response = "Hello! I'm here to help you understand your test results. What would you like to know?"
        elif 'score' in message or 'percentage' in message:
            response = "I can help you understand your test performance. What specific aspect would you like to know about?"
        elif 'wrong' in message or 'mistake' in message:
            response = "I can explain the questions you got wrong. Would you like me to go through them one by one?"
        elif 'improve' in message or 'better' in message:
            response = "To improve your performance, I recommend reviewing the questions you got wrong and practicing similar problems."
        else:
            response = "I'm here to help! You can ask me about your test scores, wrong answers, or how to improve your performance."
        
        return Response({'response': response})
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# CSRF Token view
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_csrf_token(request):
    """Get CSRF token"""
    return Response({'csrfToken': get_token(request)})

# API Views for AJAX calls
@csrf_exempt
def api_login(request):
    """API login endpoint"""
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

def api_current_user(request):
    """Get current user info"""
    if request.user.is_authenticated:
        return JsonResponse({
            'id': request.user.id,
            'username': request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'role': request.user.role
        })
    else:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

@csrf_exempt
def api_logout(request):
    """API logout endpoint"""
    logout(request)
    return JsonResponse({'success': True})

def api_subjects(request):
    """Get all subjects"""
    subjects = Subject.objects.all()
    data = [{'id': s.id, 'name': s.name, 'description': s.description} for s in subjects]
    return JsonResponse(data, safe=False)
