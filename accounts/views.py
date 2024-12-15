from .forms import CustomUserCreationForm  # カスタムフォームをインポート
from django.contrib.auth.views import LoginView
from .forms import CustomAuthenticationForm
from .models import Task, CompletedTask
from .forms import TaskCreateForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Schedule
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import CompletionForm
from datetime import date
from datetime import datetime, timedelta
import pytz
from collections import defaultdict
from django.contrib import messages
import numpy as np
from django.shortcuts import render
from .models import Task
import json
from django.utils.timezone import is_aware



def graph_view(request):
    # 学習データを取得
    tasks = CompletedTask.objects.filter(task__user=request.user)
    
    # 難易度別学習時間と課題数を集計
    difficulty_levels = [1, 2, 3, 4, 5]  # 1~5の難易度
    difficulty_hours = {level: 0 for level in difficulty_levels}
    difficulty_task_count = {level: 0 for level in difficulty_levels}
    subject_hours = {}
    completed_ratio = {"yes": 0, "no": 0}  # 完了比率の初期化

    # 理由の選択肢を取得
    reason_choices = dict(CompletedTask._meta.get_field('reason').choices)
    reason_counts = {reason: 0 for reason in reason_choices.keys()}  # 理由ごとに初期化

    for task in tasks:
        # 難易度別の集計
        if task.difficulty is not None:
            difficulty_hours[task.difficulty] += task.time_spent
            difficulty_task_count[task.difficulty] += 1
        
        # 科目別の集計
        if task.subject_name:
            if task.subject_name not in subject_hours:
                subject_hours[task.subject_name] = 0
            subject_hours[task.subject_name] += task.time_spent

        # 計画通りにできたかの比率を集計
        if task.completed_on_time == 'yes':  # 計画通りに完了
            completed_ratio["yes"] += 1
        elif task.completed_on_time == 'no':  # 計画外の場合
            completed_ratio["no"] += 1

            # 理由が登録されている場合カウント
            if task.reason in reason_choices.keys():
                reason_counts[task.reason] += 1

    # グラフデータ用に整形
    difficulty_time_data = [difficulty_hours[level] for level in difficulty_levels]
    difficulty_task_data = [difficulty_task_count[level] for level in difficulty_levels]
    subject_data = list(subject_hours.items())  # [(科目名, 学習時間), ...]
    completed_ratio_data = list(completed_ratio.values())  # [yes_count, no_count]
    reason_data = [(reason_choices[reason], count) for reason, count in reason_counts.items()]

    print(subject_data)  # 確認

    # JSON 形式に変換し、テンプレートに渡す
    context = {
        'reason_data': json.dumps(reason_data, ensure_ascii=False),  # 日本語をエスケープしない
        'difficulty_time_data': difficulty_time_data,
        'difficulty_task_data': difficulty_task_data,
        'subject_data': json.dumps(subject_data, ensure_ascii=False), 
        'completed_ratio_data': completed_ratio_data,
    }

    return render(request, 'accounts/graph_display.html', context)




def home_with_offset(request, week_offset=0):
    # 週のオフセットを使用して現在の週の日付範囲を設定
    today = date.today()
    start_of_week = today + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)

    # 1週間分の日付リストを作成
    days = [start_of_week + timedelta(days=i) for i in range(7)]
    
    # 24時間のタイムスロットリストを30分刻みで生成
    time_slots = [f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in (0, 30)]
    
    # 選択した週の範囲で作業日が設定されたタスクを取得
    tasks = Task.objects.filter(work_date__range=[start_of_week, end_of_week])

    # テンプレートに渡すデータをコンテキストとして定義
    context = {
        'days': days,
        'time_slots': time_slots,
        'tasks': tasks,
        'week_offset': week_offset,
    }
    
    return render(request, 'home.html', context)


def get_weekly_schedule(request, week_offset=0):
    # 今日の日付を基準に週の開始日を計算
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    
    # 1週間分の日付リストを生成
    days = [start_of_week + timedelta(days=i) for i in range(7)]
    
    # タイムスロットリストを1時間ごとに生成
    time_slots = ["{0:02d}:00".format(hour) for hour in range(24)]
    
    # 指定された週の日付範囲に該当するタスクを取得、日付・時間順で並べ替え
    tasks = Task.objects.filter(user=request.user, work_date__in=days).order_by('work_date', 'work_time')
    
    context = {
        'days': days,
        'time_slots': time_slots,
        'tasks': tasks,
        'week_offset': week_offset,
    }
    return render(request, 'home.html', context)


def completion_view(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        form = CompletionForm(request.POST)
        if form.is_valid():
            completed_task = form.save(commit=False)
            completed_task.task = task
            completed_task.subject_name = task.subject_name
            completed_task.assignment_name = task.assignment_name
            completed_task.user = request.user  # 現在のユーザーを設定
            completed_task.save()  # データベースに保存

            # 元のタスクの状態を更新
            task.is_completed = True
            task.save()
            return redirect('graph_display')
        else:
            print("Form is not valid:", form.errors)
            return render(request, 'accounts/completion.html', {'task': task, 'form': form})
    else:
        form = CompletionForm()
    return render(request, 'accounts/completion.html', {'task': task, 'form': form})


def diary_view(request):
    tasks = CompletedTask.objects.filter(task__user=request.user)
    return render(request, 'accounts/diary.html', {'tasks': tasks})


def home(request):
    # タイムスロットを30分刻みで設定
    time_slots = []
    start_time = datetime.strptime('08:00', '%H:%M')
    end_time = datetime.strptime('22:00', '%H:%M')
    while start_time <= end_time:
        time_slots.append(start_time.strftime('%H:%M'))
        start_time += timedelta(minutes=30)

    # 曜日を取得（例: 月曜日から日曜日）
    days = [(datetime.now() + timedelta(days=i)).date() for i in range(7)]

    # ユーザーに関連する登録されたタスクを取得
    tasks = Task.objects.filter(user=request.user)

    context = {
        'time_slots': time_slots,
        'days': days,
        'tasks': tasks,
    }
    return render(request, 'home.html', context)



def weekly_schedule(request):
    # 週間スケジュール表示ページのレンダリング
    return render(request, 'weekly_schedule.html')


def task_create(request):
    if request.method == 'POST':
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user  # ログインユーザーを設定

            # work_date と work_time を統合して aware datetime に変換
            work_date = form.cleaned_data['work_date']
            work_time = form.cleaned_data['work_time']
            naive_work_date = datetime.combine(work_date, work_time)
            task.work_date = naive_work_date if is_aware(naive_work_date) else timezone.make_aware(naive_work_date, timezone.get_current_timezone())

            # 新たに追加した終了時刻を aware datetime に変換
            end_time = form.cleaned_data['end_time']
            naive_end_date = datetime.combine(work_date, end_time)
            task.end_date = naive_end_date if is_aware(naive_end_date) else timezone.make_aware(naive_end_date, timezone.get_current_timezone())

            # deadline と deadline_time を統合して aware datetime に変換
            deadline = form.cleaned_data['deadline']
            deadline_time = form.cleaned_data['deadline_time']
            naive_deadline = datetime.combine(deadline, deadline_time)
            task.deadline = naive_deadline if is_aware(naive_deadline) else timezone.make_aware(naive_deadline, timezone.get_current_timezone())

            task.save()
            return redirect('task_list')
    else:
        form = TaskCreateForm()

    return render(request, 'accounts/task_create.html', {'form': form})


def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskCreateForm(request.POST, instance=task)
        if form.is_valid():
            # POSTデータから取得した値を処理
            work_datetime = datetime.combine(
                form.cleaned_data['work_date'], form.cleaned_data['work_time']
            )
            task.work_date = timezone.make_aware(work_datetime, timezone.get_current_timezone()) if not timezone.is_aware(work_datetime) else work_datetime

            end_datetime = datetime.combine(
                form.cleaned_data['work_date'], form.cleaned_data['end_time']
            )
            task.end_date = timezone.make_aware(end_datetime, timezone.get_current_timezone()) if not timezone.is_aware(end_datetime) else end_datetime

            deadline_datetime = datetime.combine(
                form.cleaned_data['deadline'], form.cleaned_data['deadline_time']
            )
            task.deadline = timezone.make_aware(deadline_datetime, timezone.get_current_timezone()) if not timezone.is_aware(deadline_datetime) else deadline_datetime

            task.save()
            return redirect('task_list')
    else:
        # 初期値を設定（タイムゾーンを考慮してUTCからローカル時間に変換）
        initial_data = {
            'work_date': timezone.localtime(task.work_date).date(),
            'work_time': timezone.localtime(task.work_date).time(),
            'end_time': timezone.localtime(task.end_date).time(),
            'deadline': timezone.localtime(task.deadline).date(),
            'deadline_time': timezone.localtime(task.deadline).time(),
        }
        form = TaskCreateForm(instance=task, initial=initial_data)

    return render(request, 'accounts/edit_task.html', {'form': form})

'''
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskCreateForm(request.POST, instance=task)
        if form.is_valid():
            # 時間を結合した後にタイムゾーンを適用
            work_datetime = datetime.combine(
                form.cleaned_data['work_date'], form.cleaned_data['work_time']
            )
            end_datetime = datetime.combine(
                form.cleaned_data['work_date'], form.cleaned_data['end_time']
            )
            deadline_datetime = datetime.combine(
                form.cleaned_data['deadline'], form.cleaned_data['deadline_time']
            )
            
            # タイムゾーンを設定
            task.work_date = timezone.localtime(timezone.make_aware(work_datetime, timezone.get_current_timezone()))
            task.end_date = timezone.localtime(timezone.make_aware(end_datetime, timezone.get_current_timezone()))
            task.deadline = timezone.localtime(timezone.make_aware(deadline_datetime, timezone.get_current_timezone()))
            
            form.save()
            return redirect('task_list')
    else:
        # 初期値を設定
        initial_data = {
            'work_date': task.work_date.date(),
            'work_time': task.work_date.time(),
            'end_time': task.end_date.time(),
            'deadline': task.deadline.date(),
            'deadline_time': task.deadline.time(),
        }
        form = TaskCreateForm(instance=task, initial=initial_data)

    return render(request, 'accounts/edit_task.html', {'form': form})


def task_create(request):
    if request.method == 'POST':
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user  # ログインユーザーを設定

            # work_date と work_time を統合して aware datetime に変換
            work_date = form.cleaned_data['work_date']
            work_time = form.cleaned_data['work_time']
            naive_work_date = datetime.combine(work_date, work_time)
            task.work_date = timezone.make_aware(naive_work_date, timezone.get_current_timezone())

            # 新たに追加した終了時刻を aware datetime に変換
            end_time = form.cleaned_data['end_time']
            naive_end_date = datetime.combine(work_date, end_time)
            task.end_date = timezone.make_aware(naive_end_date, timezone.get_current_timezone())

            # deadline と deadline_time を統合して aware datetime に変換
            deadline = form.cleaned_data['deadline']
            deadline_time = form.cleaned_data['deadline_time']
            naive_deadline = datetime.combine(deadline, deadline_time)
            task.deadline = timezone.make_aware(naive_deadline, timezone.get_current_timezone())

            task.save()
            return redirect('task_list')
    else:
        form = TaskCreateForm()

    return render(request, 'accounts/task_create.html', {'form': form})
'''


def task_list(request):
    # ユーザーに関連する未完了のタスクを取得
    tasks = Task.objects.filter(user=request.user, is_completed=False).order_by('work_date')
    return render(request, 'accounts/task_list.html', {'tasks': tasks})




def home_view(request, week_offset=0):
    # 週のオフセットを使用して現在の週の日付範囲を設定
    week_offset = int(week_offset)  
    if week_offset < 0:
        week_offset = 0

    # 現在の日付を取得
    today = datetime.now().date()

    # 週の始まりの日付を計算
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)

    # 1週間分の日付リストを生成
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]

    return render(request, 'accounts/task_list.html', {'week_dates': week_dates, 'week_offset': week_offset})


class CustomLoginView(LoginView):
    # カスタム認証フォームとテンプレートを使用してログイン
    form_class = CustomAuthenticationForm  
    template_name = 'registration/login.html'


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # カスタムフォームを使用
        if form.is_valid():
            form.save()
            return redirect('login')  # 登録後にログインページにリダイレクト
    else:
        form = CustomUserCreationForm()  
    return render(request, 'registration/signup.html', {'form': form})

