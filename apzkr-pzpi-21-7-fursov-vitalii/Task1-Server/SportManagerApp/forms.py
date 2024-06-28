from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, UsernameField
from .models import *

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password', 'team', 'first_name', 'age', 'gender', 'height', 'weight', 'role']

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'city', 'sport_type']

class MatchForm(forms.ModelForm):
    team1 = forms.ModelChoiceField(queryset=Team.objects.all())
    team2 = forms.ModelChoiceField(queryset=Team.objects.all())
    team1_score = forms.IntegerField()
    team2_score = forms.IntegerField()

    class Meta:
        model = Match
        fields = ['datetime', 'location', 'duration', 'competition']

    def save(self, commit=True):
        match = super().save(commit=False)
        if commit:
            match.save()
            team1, _ = MatchTeam.objects.update_or_create(
                match=match,
                team=self.cleaned_data['team1'],
                defaults={'team_score': self.cleaned_data['team1_score']}
            )
            team2, _ = MatchTeam.objects.update_or_create(
                match=match,
                team=self.cleaned_data['team2'],
                defaults={'team_score': self.cleaned_data['team2_score']}
            )
        return match

class MatchTeamForm(forms.ModelForm):
    class Meta:
        model = MatchTeam
        fields = ['match', 'team', 'team_score']

class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ['name', 'prize_pool', 'league', 'sport_type']

class TrainingForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='sportsman'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Training
        fields = ['datetime', 'location', 'duration']

    def save(self, commit=True):
        training = super().save(commit=False)
        if commit:
            training.save()
            users = self.cleaned_data['users']
            for user in users:
                UserTraining.objects.create(user=user, training=training)
        return training
        
class UserTrainingForm(forms.ModelForm):
    class Meta:
        model = UserTraining
        fields = ['user', 'sensor', 'training', 'intensity']

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ['heart_rate']

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField()
    age = forms.IntegerField()
    gender = forms.CharField()
    height = forms.IntegerField()
    weight = forms.IntegerField()

    class Meta:
        model = User
        fields = ('email', 'first_name', 'age', 'gender', 'height', 'weight', 'password1', 'password2')

class LoginUserForm(AuthenticationForm):
    username = UsernameField()
    password = forms.CharField(widget=forms.PasswordInput)
