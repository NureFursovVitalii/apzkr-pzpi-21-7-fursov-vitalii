from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from SportManagerApp import views

urlpatterns = [
    # Team URLs
    path('teams/', views.team_list, name='team_list'),
    path('teams/<int:pk>/', views.team_detail, name='team_detail'),
    path('teams/new/', views.team_create, name='team_create'),
    path('teams/<int:pk>/edit/', views.team_update, name='team_update'),
    path('teams/<int:pk>/delete/', views.team_delete, name='team_delete'),

    # Match URLs
    path('matches/', views.match_list, name='match_list'),
    path('matches/<int:pk>/', views.match_detail, name='match_detail'),
    path('matches/new/', views.match_create, name='match_create'),
    path('matches/<int:pk>/edit/', views.match_update, name='match_update'),
    path('matches/<int:pk>/delete/', views.match_delete, name='match_delete'),

    # MatchTeam URLs
    path('match-teams/', views.matchteam_list, name='matchteam_list'),
    path('match-teams/<int:pk>/', views.matchteam_detail, name='matchteam_detail'),
    path('match-teams/new/', views.matchteam_create, name='matchteam_create'),
    path('match-teams/<int:pk>/edit/', views.matchteam_update, name='matchteam_update'),
    path('match-teams/<int:pk>/delete/', views.matchteam_delete, name='matchteam_delete'),

    # Competition URLs
    path('competitions/', views.competition_list, name='competition_list'),
    path('competitions/<int:pk>/', views.competition_detail, name='competition_detail'),
    path('competitions/new/', views.competition_create, name='competition_create'),
    path('competitions/<int:pk>/edit/', views.competition_update, name='competition_update'),
    path('competitions/<int:pk>/delete/', views.competition_delete, name='competition_delete'),

    # Training URLs
    path('trainings/', views.training_list, name='training_list'),
    path('trainings/<int:year>/<int:month>/', views.training_list, name='training_list'),
    path('trainings/<int:pk>/', views.training_detail, name='training_detail'),
    path('trainings/new/<str:date>/', views.training_create, name='training_create'),
    path('trainings/<int:pk>/edit/', views.training_update, name='training_update'),
    path('trainings/<int:pk>/delete/', views.training_delete, name='training_delete'),

    # UserTraining URLs
    path('user-trainings/', views.usertraining_list, name='usertraining_list'),
    path('user-trainings/<int:pk>/', views.usertraining_detail, name='usertraining_detail'),
    path('user-trainings/new/', views.usertraining_create, name='usertraining_create'),
    path('user-trainings/<int:pk>/edit/', views.usertraining_update, name='usertraining_update'),
    path('user-trainings/<int:pk>/delete/', views.usertraining_delete, name='usertraining_delete'),

    # Sensor URLs
    path('sensors/', views.sensor_list, name='sensor_list'),
    path('sensors/<int:pk>/', views.sensor_detail, name='sensor_detail'),
    path('sensors/new/', views.sensor_create, name='sensor_create'),
    path('sensors/<int:pk>/edit/', views.sensor_update, name='sensor_update'),
    path('sensors/<int:pk>/delete/', views.sensor_delete, name='sensor_delete'),

    # User URLs
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/new/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_update, name='user_update'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),

    # Admin URL
    path('admin/', admin.site.urls),

    # Custom URLs
    path('register/', views.register, name='register'),
    path('login/', views.userlogin, name='login'),
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),
    path('csrf_token/', views.get_csrf_token, name='csrf_token'),
    path('backup/', views.backup, name='backup')
]
