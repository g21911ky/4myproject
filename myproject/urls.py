from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from accounts import views

# シンプルなホームページビュー
def home(request):
    return HttpResponse("Welcome to the Task Management System")

# ログインや登録のルーティングを設定
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # accountsアプリのURLをインクルード
    path('', home, name='home'),  # ルートURLを設定
    #path('', views.home_view, name='home'),  # トップページとして設定する場合
    path('tasks/', views.task_list, name='task_list'),
    path('home/', views.home_view, name='home'),  # homeページへのルート
    path('task/<int:task_id>/completion/', views.completion_view, name='completion_view'),
    path('task_list/', views.task_list, name='task_list'),
]