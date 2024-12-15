from django import forms # Djangoのフォーム機能をインポート
from django.contrib.auth.forms import UserCreationForm #ユーザー作成用のフォームとユーザーモデルをインポート
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm #認証用フォームをインポート
from .models import Task #自作のモデルTaskをインポート
from .models import CompletedTask
from django.utils.timezone import make_aware
from datetime import datetime
from .models import Task

class TaskCreateForm(forms.ModelForm):
    work_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="取り組む日程")
    work_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="開始時刻")
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="終了時刻")
    deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="締切日")
    deadline_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="締切")

    class Meta:
        model = Task
        fields = ['subject_name', 'assignment_name', 'work_date', 'work_time', 'end_time', 'deadline', 'deadline_time', 'memo']
        labels = {
            'subject_name': '科目名',  # 'subject_name' のラベルを変更
            'assignment_name': '課題名',  # 'assignment_name' のラベルを変更
            'deadline': '締切日程',  # 'deadline' のラベルを変更
            'deadline_time': '締切時間',
            'work_date': '取り組む日程',  # 'work_date' のラベルを変更
            'work_time': '開始時刻',
            'end_time': '終了時刻',
            'memo': 'メモ',  # 'memo' のラベルを変更
        }

    def clean(self):
        cleaned_data = super().clean()

        # 取り組む日時
        work_date = cleaned_data.get('work_date')
        work_time = cleaned_data.get('work_time')
        if work_date and work_time:
            work_datetime = datetime.combine(work_date, work_time)
            cleaned_data['work_datetime'] = make_aware(work_datetime) if work_datetime.tzinfo is None else work_datetime

        # 終了日時
        end_time = cleaned_data.get('end_time')
        if work_date and end_time:
            end_datetime = datetime.combine(work_date, end_time)
            cleaned_data['end_datetime'] = make_aware(end_datetime) if end_datetime.tzinfo is None else end_datetime

        # 締切日時
        deadline_date = cleaned_data.get('deadline')
        deadline_time = cleaned_data.get('deadline_time')
        if deadline_date and deadline_time:
            deadline_datetime = datetime.combine(deadline_date, deadline_time)
            cleaned_data['deadline_datetime'] = make_aware(deadline_datetime) if deadline_datetime.tzinfo is None else deadline_datetime

        return cleaned_data



#カスタム認証フォーム（ログイン時に使用）
class CustomAuthenticationForm(AuthenticationForm):
    #ユーザー名入力フィールド
    username = forms.CharField(
        label='ユーザー名',  
        widget=forms.TextInput(attrs={'autofocus': True}),
        help_text='ユーザー名を入力してください。' 
    )
    #パスワード入力フィールド
    password = forms.CharField(
        label='パスワード',  # パスワードフィールドのラベル
        widget=forms.PasswordInput,
        help_text='パスワードを入力してください。'  # パスワードのヘルプテキスト
    )

#カスタムユーザー作成フォーム（新規登録時に使用）
class CustomUserCreationForm(UserCreationForm):
    #パスワード1（1回目）
    password1 = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput,
        help_text=' '
    )
    #パスワード2（確認用）
    password2 = forms.CharField(
        label='パスワード（確認用）',
        widget=forms.PasswordInput,
        help_text=' '
    )

    class Meta:
        #Userモデルに関連付け
        model = User
        #対象フィールドとラベル、ヘルプテキストを設定
        fields = ('username', 'password1', 'password2')
        labels = {
            'username': 'ユーザー名',
        }
        help_texts = {
            'username': ' ',
        }

#課題完了入力用のフォーム
class CompletionForm(forms.ModelForm):
    # かかった時間の入力フィールド（整数入力、分単位）
    time_spent = forms.IntegerField(
        widget=forms.TextInput(attrs={'type': 'number', 'min': '1', 'placeholder': '例: 120'}),
        label='かかった時間（分）'
    )
    # 計画通りにできたかの確認フィールド（はい・いいえの選択肢）
    completed_on_time = forms.ChoiceField(
        choices=[('yes', 'はい'), ('no', 'いいえ')],
        label='計画通りにできましたか？'
    )
    # 難易度の入力フィールド（1～5の整数）
    difficulty = forms.IntegerField(
        widget=forms.TextInput(attrs={'type': 'number', 'min': '1', 'max': '5'}),
        label='難易度（1～5）'
    )
    # 課題に対するコメント（任意入力）
    comment = forms.CharField(widget=forms.Textarea, label='課題に対するコメント', required=False)
    # できなかった理由の入力フィールド（選択肢あり、任意）
    reason = forms.ChoiceField(
        choices=[
            ('時間がなかった', '時間がなかった'),
            ('思ったより時間がかかった', '思ったより時間がかかった'),
            ('集中できなかった', '集中できなかった'),
            ('やる気が出なかった', 'やる気が出なかった'),
            ('予想外の予定が入った', '予想外の予定が入った'),
            ('体調不良', '体調不良'),
            ('その他', 'その他')
        ],
        label='できなかった理由',
        required=False
    )
    class Meta:
        model = CompletedTask
        fields = ['time_spent', 'completed_on_time', 'reason', 'difficulty', 'comment']
