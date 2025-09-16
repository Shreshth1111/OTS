from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from OTS.models import *
import random
import time
import json
import os

# OpenAI SDK (optional; used if OPENAI_API_KEY is configured)
try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def welcome(request):
    template = loader.get_template('welcome.html')
    return HttpResponse(template.render())


def candidateRegistrationForm(request):
    return render(request, 'registration_form.html')


def candidateRegistration(request):
    if request.method == 'POST':
        username = request.POST['username']
        if Candidate.objects.filter(username=username).exists():
            userStatus = 1
        else:
            Candidate.objects.create(
                username=username,
                password=request.POST['password'],
                name=request.POST['name'],
            )
            userStatus = 2
    else:
        userStatus = 3
    return render(request, 'registration.html', {'userStatus': userStatus})


def loginView(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        candidate = Candidate.objects.filter(username=username, password=password).first()
        if not candidate:
            return render(request, 'login.html', {'loginError': "Invalid Username or Password"})
        request.session['username'] = candidate.username
        request.session['name'] = candidate.name
        return HttpResponseRedirect("home")
    return render(request, 'login.html')


def candidateHome(request):
    if 'name' not in request.session:
        return HttpResponseRedirect("login")
    candidate = Candidate.objects.get(username=request.session['username'])
    total_questions = Question.objects.count()
    return render(request, 'home.html', {'candidate': candidate, 'total_questions': total_questions})


def _compute_duration_minutes(n: int) -> int:
    config = TestConfig.objects.first()
    if config:
        if n <= 5:
            return config.minutes_short
        elif n <= 10:
            return config.minutes_medium
        else:
            return config.minutes_long
    return max(n * 1, 1)


def testPaper(request):
    if 'name' not in request.session:
        return HttpResponseRedirect("login")

    try:
        n = int(request.GET.get('n', '5'))
    except ValueError:
        n = 5

    question_pool = list(Question.objects.all())
    random.shuffle(question_pool)
    questions_list = question_pool[:n]

    duration_minutes = _compute_duration_minutes(n)
    duration_seconds = duration_minutes * 60

    # Persist timer in session
    session_key = 'current_test_timer'
    now_sec = int(time.time())
    timer = request.session.get(session_key)

    if (
        not timer
        or timer.get('n') != n
        or (now_sec - int(timer.get('start_ts', now_sec))) >= int(timer.get('duration_sec', duration_seconds))
    ):
        timer = {'n': n, 'start_ts': now_sec, 'duration_sec': duration_seconds}
        request.session[session_key] = timer
        request.session.modified = True

    elapsed = max(0, now_sec - int(timer['start_ts']))
    remaining_seconds = max(0, int(timer['duration_sec']) - elapsed)

    config = TestConfig.objects.first()
    show_leave_warning = bool(config.show_leave_warning) if config else True

    context = {
        'questions': questions_list,
        'total_questions': n,
        'time_limit_minutes': duration_minutes,
        'time_limit_seconds': remaining_seconds,
        'total_duration_seconds': int(timer['duration_sec']),
        'show_leave_warning': show_leave_warning,
    }
    return render(request, 'test_paper.html', context)


def calculateTestResult(request):
    if 'name' not in request.session:
        return HttpResponseRedirect("login")

    total_attempt = 0
    total_right = 0
    total_wrong = 0
    qid_list = []
    details = []

    for k in request.POST:
        if k.startswith('qno'):
            qid_list.append(int(request.POST[k]))

    for qid in qid_list:
        question = Question.objects.get(qid=qid)
        user_answer = request.POST.get('q' + str(qid), '').upper()
        correct_answer = (question.ans or '').upper()
        is_correct = (user_answer == correct_answer) and (user_answer != '')

        if user_answer:
            total_attempt += 1
            if is_correct:
                total_right += 1
            else:
                total_wrong += 1

        details.append({
            'qid': qid,
            'question': question.que,
            'options': {'A': question.a, 'B': question.b, 'C': question.c, 'D': question.d},
            'correct': correct_answer,
            'user': user_answer or '-',
            'is_correct': is_correct
        })

    total_questions = max(len(qid_list), 1)
    points = (total_right - total_wrong) / total_questions * 10

    result = Result(
        username=Candidate.objects.get(username=request.session['username']),
        attempt=total_attempt,
        right=total_right,
        wrong=total_wrong,
        points=points,
        details=details
    )
    result.save()

    candidate = Candidate.objects.get(username=request.session['username'])
    candidate.test_attempted += 1
    candidate.points = (candidate.points * (candidate.test_attempted - 1) + points) / candidate.test_attempted
    candidate.save()

    if 'current_test_timer' in request.session:
        try:
            del request.session['current_test_timer']
        except KeyError:
            pass

    return HttpResponseRedirect('result')


def testResultHistory(request):
    if 'name' not in request.session:
        return HttpResponseRedirect("login")
    candidate = Candidate.objects.get(username=request.session['username'])
    results = Result.objects.filter(username_id=candidate.username)
    return render(request, 'candidate_history.html', {'candidate': candidate, 'results': results})


def testDetail(request):
    if 'name' not in request.session:
        return HttpResponseRedirect("login")

    username = request.session['username']
    rid = request.GET.get('resultid')
    if rid:
        try:
            result = Result.objects.get(resultid=int(rid), username_id=username)
        except Result.DoesNotExist:
            return HttpResponseRedirect("test-history")
    else:
        result = Result.objects.filter(username_id=username).order_by('-resultid').first()
        if not result:
            return HttpResponseRedirect("test-history")

    candidate = Candidate.objects.get(username=username)
    return render(request, 'test_detail.html', {'candidate': candidate, 'result': result})


def showTestResult(request):
    if 'name' not in request.session:
        return HttpResponseRedirect("login")
    latest = Result.objects.filter(username_id=request.session['username']).order_by('-resultid')[:1]
    return render(request, 'show_result.html', {'result': latest})


def logoutView(request):
    if 'name' in request.session:
        if 'current_test_timer' in request.session:
            try:
                del request.session['current_test_timer']
            except KeyError:
                pass
        del request.session['username']
        del request.session['name']
    return HttpResponseRedirect("login")


def _summarize_mistakes(result: Result):
    wrongs = [d for d in (result.details or []) if not d.get('is_correct')]
    if not wrongs:
        return "Great job! There are no mistakes in your latest test."
    lines = []
    for idx, d in enumerate(wrongs, start=1):
        correct_opt = d.get('correct')
        correct_text = d.get('options', {}).get(correct_opt, '')
        lines.append(f"{idx}. Q{d.get('qid')} — Correct: {correct_opt}) {correct_text}")
    return "Here are your mistakes and the correct answers:\n" + "\n".join(lines)


def _openai_client():
    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key or OpenAI is None:
        return None
    return OpenAI(api_key=api_key)


def _openai_chat_reply(user_message: str, result: Result) -> str:
    client = _openai_client()
    if client is None:
        return ""

    summary = {
        "attempt": result.attempt,
        "right": result.right,
        "wrong": result.wrong,
        "points": round(result.points, 2),
        "questions": [
            {
                "qid": d.get("qid"),
                "question": d.get("question"),
                "user": d.get("user"),
                "correct": d.get("correct"),
                "is_correct": d.get("is_correct"),
            }
            for d in (result.details or [])
        ][:50]
    }

    system = (
        "You are a helpful test review assistant. "
        "Explain clearly, be concise, and encourage learning. "
        "When explaining a question, identify it by qid and why the correct choice is correct. "
        "If the student was wrong, gently point out the mistake and how to avoid it next time."
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=600,
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": (
                        "Here is my latest test summary (JSON):\n"
                        f"{json.dumps(summary, ensure_ascii=False)}\n\n"
                        f"My question: {user_message}"
                    )
                }
            ],
        )
        reply = (completion.choices[0].message.content or "").strip()
        return reply or ""
    except Exception:
        return ""


@csrf_exempt
def api_chatbot(request):
    """
    Chatbot API:
    - If OPENAI_API_KEY is set, uses OpenAI to respond with test-aware help.
    - Otherwise, falls back to a simple rule-based answer.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = {}

    message = (data.get('message') or '').strip()
    rid = data.get('resultid')
    username = request.session.get('username')

    if not username:
        return JsonResponse({'reply': "Please log in to use the test assistant."}, status=401)

    result = None
    if rid:
        try:
            result = Result.objects.get(resultid=int(rid), username_id=username)
        except Result.DoesNotExist:
            result = None
    if not result:
        result = Result.objects.filter(username_id=username).order_by('-resultid').first()
        if not result:
            return JsonResponse({'reply': "You haven't taken any tests yet. Take a test first!"})

    # Try OpenAI first
    ai_reply = _openai_chat_reply(message, result)
    if ai_reply:
        return JsonResponse({'reply': ai_reply})

    # Fallback rule-based
    lower = message.lower()
    if any(k in lower for k in ['hello', 'hi', 'hey']):
        reply = "Hello! I can explain your score, list mistakes, or explain a specific question. Try: 'show my mistakes' or 'explain question 12'."
    elif any(k in lower for k in ['score', 'points', 'how did i do', 'result']):
        reply = f"You attempted {result.attempt} questions. Correct: {result.right}, Wrong: {result.wrong}. Points: {round(result.points, 2)} / 10."
    elif any(k in lower for k in ['mistake', 'mistakes', 'wrong']):
        reply = _summarize_mistakes(result)
    elif 'explain question' in lower:
        num = ''.join([c for c in lower if c.isdigit()])
        if num:
            qid = int(num)
            detail = next((d for d in (result.details or []) if d.get('qid') == qid), None)
            if detail:
                correct_opt = detail.get('correct')
                correct_text = detail.get('options', {}).get(correct_opt, '')
                user_opt = detail.get('user')
                user_text = detail.get('options', {}).get(user_opt, '')
                reply = (
                    f"Q{qid}: {detail.get('question')}\n"
                    f"Your answer: {user_opt}) {user_text or ''}\n"
                    f"Correct answer: {correct_opt}) {correct_text}\n"
                    f"{'You were correct!' if detail.get('is_correct') else 'This is the correct choice because it best matches the question.'}"
                )
            else:
                reply = f"I couldn't find details for question {qid} in your latest test."
        else:
            reply = "Please specify the question number, e.g., 'explain question 12'."
    else:
        reply = "I can help with: 'show my mistakes', 'explain question 7', or 'what is my score?'."

    return JsonResponse({'reply': reply})


def chatbot_page(request):
    if 'name' not in request.session:
        return HttpResponseRedirect("login")
    username = request.session['username']
    result = Result.objects.filter(username_id=username).order_by('-resultid').first()
    return render(request, 'chatbot.html', {'result': result})
