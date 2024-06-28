from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.views import View
from django.contrib.auth.decorators import login_required
from .models import User, Team, Match, MatchTeam, Competition, Training, UserTraining, Sensor
from django.db.models import Avg, Count, F, Q, Sum, FloatField
from .forms import UserForm, TeamForm, MatchForm, MatchTeamForm, CompetitionForm, TrainingForm, UserTrainingForm, SensorForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import RegisterUserForm, LoginUserForm
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.contrib import messages
from django.core.management import call_command
from io import StringIO
import calendar
from django.utils.timezone import now
from datetime import date, datetime, timedelta
from itertools import groupby

# Generating CSRF token
def get_csrf_token(request):
    return JsonResponse({'csrf_token': get_token(request)})

# Making a backup of the database
def backup(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return HttpResponseForbidden("You are not authorized to perform this action.")
    
    out = StringIO()
    call_command('backup', stdout=out)
    messages.success(request, 'Backup completed successfully')
    return redirect('home')

# Redirect to the home page
def home(request):
    return redirect('competition_list')

# Registration
def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'sportsman'
            user.save()
            return redirect('login')
    else:
        form = RegisterUserForm()
    return render(request, 'SportManagerApp/register.html', {'form': form})

# Authorization
def userlogin(request):
    if request.method == 'POST':
        form = LoginUserForm(request, request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginUserForm()
    return render(request, 'SportManagerApp/login.html', {'form': form})

# Log out of account
def logout(request):
    return redirect('login')

# User Views
@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'SportManagerApp/user_list.html', {'users': users})

def generate_training_recommendation(trainings, user):
    mhr = 220 - user.age
    moderate_min = 0.5 * mhr
    moderate_max = 0.7 * mhr
    high_min = 0.7 * mhr
    high_max = 0.85 * mhr

    moderate_count = 0
    high_count = 0

    for training in trainings:
        if moderate_min <= training.intensity <= moderate_max:
            moderate_count += 1
        elif high_min <= training.intensity <= high_max:
            high_count += 1

    total_trainings = len(trainings)

    if total_trainings == 0:
        recommendation = "No recent training data available."
    else:
        moderate_ratio = moderate_count / total_trainings
        high_ratio = high_count / total_trainings

        if moderate_ratio > 0.5:
            recommendation = "You are doing a good amount of moderate intensity training. Keep it up!"
        elif high_ratio > 0.5:
            recommendation = "You are doing a lot of high intensity training. Consider incorporating more moderate intensity sessions."
        else:
            recommendation = "Your training intensity is well balanced. Continue with your current routine."

    return recommendation

@login_required
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    trainings = UserTraining.objects.filter(user=user).order_by('-training__datetime')[:10]

    recommendation = generate_training_recommendation(trainings, user)

    return render(request, 'SportManagerApp/user_detail.html', {
        'user': user,
        'trainings': trainings,
        'recommendation': recommendation
    })


@login_required
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'SportManagerApp/user_form.html', {'form': form})

@login_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'SportManagerApp/user_form.html', {'form': form})

@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return redirect('user_list')

# Team Views
@login_required
def team_list(request):
    teams = Team.objects.all()
    return render(request, 'SportManagerApp/team_list.html', {'teams': teams})

@login_required
def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    stats = team_statistics(pk)
    return render(request, 'SportManagerApp/team_detail.html', {'team': team, 'stats': stats})

@login_required
def team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('team_list')
    else:
        form = TeamForm()
    return render(request, 'SportManagerApp/team_form.html', {'form': form})

@login_required
def team_update(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            return redirect('team_list')
    else:
        form = TeamForm(instance=team)
    return render(request, 'SportManagerApp/team_form.html', {'form': form})

@login_required
def team_delete(request, pk):
    team = get_object_or_404(Team, pk=pk)
    team.delete()
    return redirect('team_list')

# Match Views
@login_required
def match_list(request):
    matches = Match.objects.all()
    return render(request, 'SportManagerApp/match_list.html', {'matches': matches})

@login_required
def match_create(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('match_list')
    else:
        form = MatchForm()
    return render(request, 'SportManagerApp/match_form.html', {'form': form})

@login_required
def match_update(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            return redirect('match_list')
    else:
        match_teams = match.matchteam_set.all()
        initial_data = {
            'team1': match_teams[0].team if match_teams else None,
            'team2': match_teams[1].team if match_teams else None,
            'team1_score': match_teams[0].team_score if match_teams else None,
            'team2_score': match_teams[1].team_score if match_teams else None,
        }
        form = MatchForm(instance=match, initial=initial_data)
    return render(request, 'SportManagerApp/match_form.html', {'form': form})

@login_required
def match_delete(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == 'POST':
        match.delete()
        return redirect('match_list')
    return render(request, 'SportManagerApp/match_confirm_delete.html', {'match': match})

@login_required
def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    return render(request, 'SportManagerApp/match_detail.html', {'match': match})

# MatchTeam Views
@login_required
def matchteam_list(request):
    matchteams = MatchTeam.objects.all()
    return render(request, 'SportManagerApp/matchteam_list.html', {'matchteams': matchteams})

@login_required
def matchteam_detail(request, pk):
    matchteam = get_object_or_404(MatchTeam, pk=pk)
    return render(request, 'SportManagerApp/matchteam_detail.html', {'matchteam': matchteam})

@login_required
def matchteam_create(request):
    if request.method == 'POST':
        form = MatchTeamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('matchteam_list')
    else:
        form = MatchTeamForm()
    return render(request, 'SportManagerApp/matchteam_form.html', {'form': form})

@login_required
def matchteam_update(request, pk):
    matchteam = get_object_or_404(MatchTeam, pk=pk)
    if request.method == 'POST':
        form = MatchTeamForm(request.POST, instance=matchteam)
        if form.is_valid():
            form.save()
            return redirect('matchteam_list')
    else:
        form = MatchTeamForm(instance=matchteam)
    return render(request, 'SportManagerApp/matchteam_form.html', {'form': form})

@login_required
def matchteam_delete(request, pk):
    matchteam = get_object_or_404(MatchTeam, pk=pk)
    matchteam.delete()
    return redirect('matchteam_list')

# Competition Views
def competition_list(request):
    competitions = Competition.objects.all()
    return render(request, 'SportManagerApp/competition_list.html', {'competitions': competitions})

def competition_detail(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    matches = Match.objects.filter(competition_id=competition.competition_id)
    match_results = []

    for match in matches:
        teams = MatchTeam.objects.filter(match_id=match.match_id)
        if len(teams) == 2:
            match_results.append({
                'team1': teams[0].team.name,
                'score1': teams[0].team_score,
                'team2': teams[1].team.name,
                'score2': teams[1].team_score,
                'duration': match.duration,
                'location': match.location,
            })

    return render(request, 'SportManagerApp/competition_detail.html', {
        'competition': competition,
        'matches': match_results,
    })

def competition_create(request):
    if request.method == 'POST':
        form = CompetitionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('competition_list')
        else:
            print(form.errors)
    else:
        form = CompetitionForm()
    return render(request, 'SportManagerApp/competition_form.html', {'form': form})

def competition_update(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    if request.method == 'POST':
        form = CompetitionForm(request.POST, instance=competition)
        if form.is_valid():
            form.save()
            return redirect('competition_list')
    else:
        form = CompetitionForm(instance=competition)
    return render(request, 'SportManagerApp/competition_form.html', {'form': form})

def competition_delete(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    competition.delete()
    return redirect('competition_list')

# Training Views
@login_required
def training_list(request, year=None, month=None):
    if year is None or month is None:
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
    else:
        year = int(year)
        month = int(month)

    current_month = datetime(year, month, 1)
    next_month = current_month + timedelta(days=31)
    previous_month = current_month - timedelta(days=1)
    
    days_in_calendar = []
    start_day = current_month
    end_day = next_month - timedelta(days=1)

    while start_day <= end_day:
        day_trainings = Training.objects.filter(datetime__date=start_day)
        days_in_calendar.append({'date': start_day, 'trainings': day_trainings})
        start_day += timedelta(days=1)

    context = {
        'current_year': current_month.year,
        'current_month': current_month.strftime('%B'),
        'next_month': next_month,
        'previous_month': previous_month,
        'days_in_calendar': days_in_calendar,
        'user': request.user  
    }

    return render(request, 'SportManagerApp/training_list.html', context)


@login_required
def training_detail(request, pk):
    training = get_object_or_404(Training, pk=pk)
    user_trainings = UserTraining.objects.filter(training=training)
    return render(request, 'SportManagerApp/training_detail.html', {'training': training, 'user_trainings': user_trainings})

@login_required
def training_create(request, date):
    training_date = datetime.strptime(date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
    initial_data = {'datetime': training_date}

    if request.method == "POST":
        form = TrainingForm(request.POST)
        if form.is_valid():
            training = form.save(commit=False)
            training.datetime = training_date  
            training.save()
            form.save_m2m()  
            return redirect('training_list')
    else:
        form = TrainingForm(initial=initial_data)
    
    return render(request, 'SportManagerApp/training_form.html', {'form': form})

@login_required
def training_update(request, pk):
    if request.user.role not in ['admin', 'coach']:
        return redirect('home')
    training = get_object_or_404(Training, pk=pk)
    if request.method == 'POST':
        form = TrainingForm(request.POST, instance=training)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TrainingForm(instance=training)
    return render(request, 'SportManagerApp/training_form.html', {'form': form, 'training': training})

@login_required
def training_delete(request, pk):
    if request.user.role not in ['admin', 'coach']:
        return redirect('home')
    training = get_object_or_404(Training, pk=pk)
    if request.method == 'POST':
        training.delete()
        return redirect('home')
    return render(request, 'SportManagerApp/training_confirm_delete.html', {'training': training})

# UserTraining Views
@login_required
def usertraining_list(request):
    usertrainings = UserTraining.objects.all()
    return render(request, 'SportManagerApp/usertraining_list.html', {'usertrainings': usertrainings})

@login_required
def usertraining_detail(request, pk):
    usertraining = get_object_or_404(UserTraining, pk=pk)
    return render(request, 'SportManagerApp/usertraining_detail.html', {'usertraining': usertraining})

@login_required
def usertraining_create(request):
    if request.method == 'POST':
        form = UserTrainingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usertraining_list')
    else:
        form = UserTrainingForm()
    return render(request, 'SportManagerApp/usertraining_form.html', {'form': form})

@login_required
def usertraining_update(request, pk):
    usertraining = get_object_or_404(UserTraining, pk=pk)
    if request.method == 'POST':
        form = UserTrainingForm(request.POST, instance=usertraining)
        if form.is_valid():
            form.save()
            return redirect('usertraining_list')
    else:
        form = UserTrainingForm(instance=usertraining)
    return render(request, 'SportManagerApp/usertraining_form.html', {'form': form})

@login_required
def usertraining_delete(request, pk):
    usertraining = get_object_or_404(UserTraining, pk=pk)
    usertraining.delete()
    return redirect('usertraining_list')

# Sensor Views
@login_required
def sensor_list(request):
    sensors = Sensor.objects.all()
    return render(request, 'SportManagerApp/sensor_list.html', {'sensors': sensors})

@login_required
def sensor_detail(request, pk):
    sensor = get_object_or_404(Sensor, pk=pk)
    return render(request, 'SportManagerApp/sensor_detail.html', {'sensor': sensor})

@login_required
def sensor_create(request):
    if request.method == 'POST':
        form = SensorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sensor_list')
    else:
        form = SensorForm()
    return render(request, 'SportManagerApp/sensor_form.html', {'form': form})

@login_required
def sensor_update(request, pk):
    sensor = get_object_or_404(Sensor, pk=pk)
    if request.method == 'POST':
        form = SensorForm(request.POST, instance=sensor)
        if form.is_valid():
            form.save()
            return redirect('sensor_list')
    else:
        form = SensorForm(instance=sensor)
    return render(request, 'SportManagerApp/sensor_form.html', {'form': form})

@login_required
def sensor_delete(request, pk):
    sensor = get_object_or_404(Sensor, pk=pk)
    sensor.delete()
    return redirect('sensor_list')

# Statistics of the team
def team_statistics(team_id):
    # 1. Number of competitions the team participated in
    competitions_count = MatchTeam.objects.filter(team_id=team_id).values('match__competition').distinct().count()

    # 2. The most successful competition
    competition_scores = (
        MatchTeam.objects.filter(team_id=team_id)
        .values('match__competition__name')
        .annotate(total_score=Sum('team_score'))
        .order_by('-total_score')
    )
    most_successful_competition = competition_scores[0]['match__competition__name'] if competition_scores else None
    most_successful_competition_score = competition_scores[0]['total_score'] if competition_scores else 0

    # 3. Average age of team members
    average_age = User.objects.filter(team_id=team_id).aggregate(Avg('age'))['age__avg']

    # 4. Team's win percentage
    total_matches = MatchTeam.objects.filter(team_id=team_id).count()
    won_matches = MatchTeam.objects.filter(
        team_id=team_id,
        team_score__gt=F('match__matchteam__team_score')
    ).count()
    win_percentage = (won_matches / total_matches * 100) if total_matches > 0 else 0

    # 5. Average goals (or points) per match
    average_goals_per_match = MatchTeam.objects.filter(team_id=team_id).aggregate(Avg('team_score'))['team_score__avg']
    
    return {
        'competitions_count': competitions_count,
        'most_successful_competition': most_successful_competition,
        'most_successful_competition_score': most_successful_competition_score,
        'average_age': average_age,
        'win_percentage': win_percentage,
        'average_goals_per_match': average_goals_per_match,
    }


