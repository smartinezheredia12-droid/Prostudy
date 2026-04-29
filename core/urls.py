from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('folders/', views.folders_view, name='folders'),
    path('folders/create/', views.folder_create, name='folder_create'),
    path('folders/<int:pk>/delete/', views.folder_delete, name='folder_delete'),
    path('folders/<int:pk>/', views.folder_detail, name='folder_detail'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/complete/', views.task_complete, name='task_complete'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('leagues/', views.leagues_view, name='leagues'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/send-message/', views.admin_send_message, name='admin_send_message'),
    path('admin-panel/adjust-xp/', views.admin_adjust_xp, name='admin_adjust_xp'),
    path('admin-panel/change-password/', views.admin_change_password, name='admin_change_password'),
    path('admin-panel/delete-user/<int:pk>/', views.admin_delete_user, name='admin_delete_user'),
]
