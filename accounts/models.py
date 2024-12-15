from django.contrib.auth.models import User
from django.db import models
#from .models import Task

#ユーザーのスケジュールを管理するためのScheduleモデル
class Schedule(models.Model):
    #ユーザー情報へのリレーション。ユーザーが削除されると関連するスケジュールも削除される
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    #スケジュールの日付
    date = models.DateField()
    #スケジュールの開始時間
    start_time = models.TimeField()
    #スケジュールの終了時間
    end_time = models.TimeField()
    #スケジュールのタスク名
    task_name = models.CharField(max_length=100)


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    assignment_name = models.CharField(max_length=100)
    work_date = models.DateTimeField()  # 日時を統合して保存
    end_date = models.DateTimeField()  # 終了時刻を追加
    deadline = models.DateTimeField()  # 日時を統合して保存
    memo = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject_name} - {self.assignment_name}"



class CompletedTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=255)
    assignment_name = models.CharField(max_length=255)
    time_spent = models.IntegerField()  # 分単位
    completed_on_time = models.CharField(max_length=10, choices=[('yes', 'はい'), ('no', 'いいえ')])
    difficulty = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    reason = models.CharField(
        max_length=50,
        choices=[
            ('時間がなかった', '時間がなかった'),
            ('思ったより時間がかかった', '思ったより時間がかかった'),
            ('集中できなかった', '集中できなかった'),
            ('やる気が出なかった', 'やる気が出なかった'),
            ('予想外の予定が入った', '予想外の予定が入った'),
            ('体調不良', '体調不良'),
            ('その他', 'その他'),
        ],
        blank=True,
        null=True,
    )

