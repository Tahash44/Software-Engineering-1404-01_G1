from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from core.auth import api_login_required
from django.contrib.auth.decorators import login_required

from core.urls import urlpatterns
from .models import UserSession, Passage, Question, Option
from django.shortcuts import get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import Passage, Question, UserSession, UserAnswer, AntiCheatLog
import json
from .models import UserSession, Question, Option, UserAnswer  # این خط تکراری است و می‌تواند حذف شود

TEAM_NAME = "team14"


@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    return render(request, f"{TEAM_NAME}/index.html")


def training_levels(request):
    return render(request, 'team14/training_levels.html')


def index(request):
    last_session = UserSession.objects.filter(
        user=request.user,  # فرض شده request.user یک User مدل معتبر است.
        mode='exam',
        end_time__isnull=False,
        scaled_score__isnull=False
    ).order_by('-end_time').first()

    context = {
        'last_score': last_session.scaled_score if last_session else None,
        'has_taken_exam': last_session is not None
    }

    return render(request, 'team14/index.html', context)


# این خط باید به decorator بالای هر تابع اضافه شود نه به صورت جداگانه.
# login_required(login_url='auth')


def easy_level(request):
    # گرفتن تمام passage های سطح آسان
    passages = Passage.objects.filter(
        difficulty_level='easy'
    ).prefetch_related('questions__options').order_by('-created_at')

    # آماده کردن داده‌ها برای ارسال به template
    passages_data = []
    for passage in passages:
        # شمارش تعداد سوالات
        question_count = passage.questions.count()

        # محاسبه زمان تخمینی (حدود 1 دقیقه برای هر 75 کلمه + 1 دقیقه برای هر سوال)
        estimated_time = (passage.text_length // 75) + question_count

        passages_data.append({
            'id': passage.id,
            'title': passage.title,
            'topic': passage.get_topic_display(),  # نمایش نام فارسی topic
            'text_length': passage.text_length,
            'question_count': question_count,
            'estimated_time': estimated_time,
            'icon': get_topic_icon(passage.topic),  # تابع کمکی برای آیکون
        })

    context = {
        'passages': passages_data,
        'difficulty': 'آسان',
        'total_passages': len(passages_data),
    }

    return render(request, 'team14/practice_passages.html', context)


def mid_level(request):
    # گرفتن تمام passage های سطح متوسط
    passages = Passage.objects.filter(
        difficulty_level='medium'
    ).prefetch_related('questions__options').order_by('-created_at')

    passages_data = []
    for passage in passages:
        question_count = passage.questions.count()
        estimated_time = (passage.text_length // 75) + question_count

        passages_data.append({
            'id': passage.id,
            'title': passage.title,
            'topic': passage.get_topic_display(),
            'text_length': passage.text_length,
            'question_count': question_count,
            'estimated_time': estimated_time,
            'icon': get_topic_icon(passage.topic),
        })

    context = {
        'passages': passages_data,
        'difficulty': 'متوسط',
        'total_passages': len(passages_data),
    }

    return render(request, 'team14/practice_passages.html', context)


def hard_level(request):
    # گرفتن تمام passage های سطح سخت
    passages = Passage.objects.filter(
        difficulty_level='hard'
    ).prefetch_related('questions__options').order_by('-created_at')

    passages_data = []
    for passage in passages:
        question_count = passage.questions.count()
        estimated_time = (passage.text_length // 75) + question_count

        passages_data.append({
            'id': passage.id,
            'title': passage.title,
            'topic': passage.get_topic_display(),
            'text_length': passage.text_length,
            'question_count': question_count,
            'estimated_time': estimated_time,
            'icon': get_topic_icon(passage.topic),
        })

    context = {
        'passages': passages_data,
        'difficulty': 'سخت',
        'total_passages': len(passages_data),
    }

    return render(request, 'team14/practice_passages.html', context)


def get_topic_icon(topic):
    icons = {
        'biology': '🧬',
        'history': '📜',
        'astronomy': '🌌',
        'geology': '🌍',
        'anthropology': '🗿',
    }
    return icons.get(topic, '📚')


def Exam_Page(request):
    return render(request, 'team14/Exam_Page.html')

@login_required(login_url='/auth/')
def practice_page(request, passage_id):
    if not request.user.is_authenticated:
        return redirect('login')

    passage = get_object_or_404(
        Passage.objects.prefetch_related('questions__options'),
        id=passage_id
    )

    questions_qs = passage.questions.all().order_by('id')

    # ✅ JSON برای JS
    questions_data = []
    for q in questions_qs:
        questions_data.append({
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": [
                {"id": opt.id, "text": opt.text}
                for opt in q.options.all()
            ]
        })

    # ✅ استفاده درست از user_id
    # در اینجا باید از request.user استفاده کنید نه از request.user.id
    # چون UserSession دارای ForeignKey به User است، بهتر است نمونه User را پاس دهید.
    # اگر user_id در مدل UserSession به صورت CharField با max_length=36 ذخیره می‌شود،
    # و شما قصد دارید شناسه کاربر را به صورت رشته‌ای ذخیره کنید، پس استفاده از request.user.id صحیح است.
    # اما اگر ForeignKey به مدل User است، باید خود شیء User را پاس دهید.
    # با توجه به تعریف UserSession که user_id: models.CharField است، request.user.id درست است.
    session, created = UserSession.objects.get_or_create(
        user_id=request.user.id,
        passage=passage,
        mode='practice',
        defaults={'start_time': timezone.now()}
    )

    user_answers = {
        ans.question_id: ans.selected_option_id
        for ans in UserAnswer.objects.filter(session=session)
    }

    elapsed = (timezone.now() - session.start_time).seconds
    time_left = max(0, 18 * 60 - elapsed)

    context = {
        'passage': passage,
        'questions': json.dumps(questions_data),
        'total_questions': questions_qs.count(),
        'session': session,
        'user_answers': json.dumps(user_answers),
        'time_left': time_left,
    }

    return render(request, 'team14/Practice_Page.html', context)


@csrf_exempt
def submit_answer(request):
    if request.method != 'POST' or not request.user.is_authenticated:
        return JsonResponse({'success': False}, status=403)

    try:
        data = json.loads(request.body)

        session = get_object_or_404(
            UserSession,
            id=data['session_id'],
            user_id=str(request.user.id)
        )

        question = get_object_or_404(
            Question,
            id=data['question_id'],
            passage=session.passage
        )

        option_id = data.get('option_id')  # ✅ ممکن است None باشد

        # ✅ استفاده از update_or_create برای کد تمیزتر
        user_answer, created = UserAnswer.objects.update_or_create(
            session=session,
            question=question,
            defaults={'selected_option_id': option_id}
        )

        # ✅ شمارش تغییرات (فقط اگر تغییر کرده باشد)
        if not created:
            user_answer.changed_count += 1
            user_answer.save(update_fields=['changed_count'])

        return JsonResponse({'success': True})

    except Exception as e:
        print(f"❌ Error in submit_answer: {e}")  # ✅ لاگ خطا
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def finish_practice(request, session_id):
    session = get_object_or_404(
        UserSession,
        id=session_id,
        user_id=str(request.user.id)  # ✅ باز هم، اطمینان از نوع داده
    )

    answers = UserAnswer.objects.filter(session=session)
    correct_count = 0

    for answer in answers:
        # اگر selected_option null باشد، این شرط اجرا نمی‌شود
        # و is_correct به صورت پیش‌فرض False خواهد ماند یا باید صراحتاً False شود.
        if answer.selected_option and answer.selected_option.is_correct:
            correct_count += 1
            answer.is_correct = True
        else:
            answer.is_correct = False
        answer.save()

    total_questions = session.passage.questions.count()

    # اطمینان از اینکه session.total_score و session.end_time فقط یک بار مقداردهی می‌شوند
    # و اگر قبلاً اتمام یافته، دوباره تغییر نکند، مگر اینکه منطق خاصی برای re-evaluate باشد.
    if session.end_time is None:  # فقط اگر هنوز تمام نشده باشد
        if total_questions > 0:
            session.total_score = (correct_count / total_questions) * 100
        else:
            session.total_score = 0  # اگر سوالی نباشد نمره 0
        session.end_time = timezone.now()
        session.save()

    return redirect('practice_result', session_id=session.id)


def practice_result(request, session_id):
    session = get_object_or_404(
        UserSession,
        id=session_id,
        user_id=str(request.user.id)
    )

    questions = Question.objects.filter(
        passage=session.passage
    ).prefetch_related('options').order_by('id')

    # ✅ گرفتن تمام پاسخ‌های کاربر به صورت QuerySet
    user_answers = UserAnswer.objects.filter(
        session=session
    ).select_related('selected_option', 'question')

    # ✅ ساخت دیکشنری از پاسخ‌ها (برای دسترسی سریع‌تر)
    answers_dict = {
        ua.question_id: ua
        for ua in user_answers
    }

    result_data = []
    correct_count = 0

    for q in questions:
        correct_option = q.options.filter(is_correct=True).first()

        # ✅ گرفتن شیء UserAnswer (نه فقط ID)
        user_answer = answers_dict.get(q.id)

        # ✅ بررسی وجود پاسخ و selected_option
        if user_answer and user_answer.selected_option:
            user_option_text = user_answer.selected_option.text
            is_correct = user_answer.selected_option.is_correct
        else:
            user_option_text = "بدون پاسخ"
            is_correct = False

        if is_correct:
            correct_count += 1

        result_data.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "correct_option": correct_option.text if correct_option else "—",
            "user_option": user_option_text,
            "is_correct": is_correct
        })

    return render(request, "team14/practice_result.html", {
        "session": session,
        "total_questions": questions.count(),
        "correct_count": correct_count,
        "results": result_data,
        "level": session.passage.get_difficulty_level_display()
    })


def about(request):
    return None
def start_learning(request):
    return None

