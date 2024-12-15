from django.urls import path
from django.contrib.auth import views as auth_views  # Django組み込みの認証ビューをインポート
from .views import CustomLoginView  # カスタムログインビュー
from .views import home
from accounts import views  # アカウント関連のビューをインポート
from django.contrib import admin
from .views import diary_view, graph_view  # 日記画面、グラフ表示画面のビュー
from .views import completion_view
from .views import home_view

# アプリケーションのURLパターンの定義
urlpatterns = [
    # ログイン画面のURL（Django組み込みのログインビューを使用）
    path('login/', auth_views.LoginView.as_view(), name='login'),
    # ログアウト画面のURL（Django組み込みのログアウトビューを使用）
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # カスタムログインビューを指定（上書きされるので1つだけ残すと良い）
    path('login/', CustomLoginView.as_view(), name='login'),
    # ユーザー登録画面（サインアップ）のURL
    path('signup/', views.signup, name='signup'),
    # ホーム画面のURL
    path('', views.home_view, name='home'),
    # 週間スケジュール画面のURL
    path('weekly_schedule/', views.weekly_schedule, name='weekly_schedule'),
    # 課題リスト画面のURL
    path('task_list/', views.task_list, name='task_list'),
    # 課題作成画面のURL
    path('tasks/create/', views.task_create, name='task_create'),
    # 課題編集画面のURL（課題IDを受け取る）
    path('edit_task/<int:task_id>/', views.edit_task, name='edit_task'),
    # 日記画面のURL
    path('diary/', diary_view, name='diary'),
    # グラフ表示画面のURL
    path('graph_display/', graph_view, name='graph_display'),
    # 課題完了画面のURL（課題IDを受け取る）
    #path('completion/<int:task_id>/', completion_view, name='completion_view'),
    path('completion/<int:task_id>/', views.completion_view, name='completion_view'),
    # 週のオフセットを設定できるホーム画面のURL
    path('home/<str:week_offset>/', views.home_view, name='home_with_offset'),
    # デフォルトの週オフセットを0に設定したホーム画面のURL
    path('home/', views.home_view, {'week_offset': 0}, name='home'),

    
]