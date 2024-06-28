from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)
    height = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()
    role = models.CharField(max_length=50, default='sportsman')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'age', 'gender', 'height', 'weight', 'role']

    def __str__(self):
        return self.email

class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    sport_type = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Match(models.Model):
    match_id = models.AutoField(primary_key=True)
    datetime = models.DateTimeField()
    location = models.CharField(max_length=100)
    duration = models.DurationField()
    competition = models.ForeignKey('Competition', on_delete=models.CASCADE)

    def __str__(self):
        return f'Match {self.match_id}'

class MatchTeam(models.Model):
    match_team_id = models.AutoField(primary_key=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    team_score = models.PositiveIntegerField()

    def __str__(self):
        return f'Match {self.match.match_id} - Team {self.team.name}'

class Competition(models.Model):
    competition_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    prize_pool = models.DecimalField(max_digits=10, decimal_places=2)
    league = models.CharField(max_length=100)
    sport_type = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Training(models.Model):
    training_id = models.AutoField(primary_key=True)
    datetime = models.DateTimeField()
    location = models.CharField(max_length=100)
    duration = models.DurationField()

    def __str__(self):
        return f'Training {self.training_id}'

class UserTraining(models.Model):
    user_training_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sensor = models.ForeignKey('Sensor', on_delete=models.CASCADE, default=1)
    training = models.ForeignKey(Training, on_delete=models.CASCADE)
    intensity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'User {self.user.email} - Training {self.training.training_id}'

class Sensor(models.Model):
    sensor_id = models.AutoField(primary_key=True)
    heart_rate = models.PositiveIntegerField()

    def __str__(self):
        return f'Sensor {self.sensor_id}'