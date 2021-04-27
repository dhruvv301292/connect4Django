import datetime

from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    image = models.ImageField(default='connect4/static/connect4/images/profile.jpg',
                             upload_to="connect4/static/connect4/images", blank=True)
    content_type = models.CharField(max_length=50, default='image/jpeg', blank=True)
    primary_color = models.CharField(max_length=7, blank=True)
    secondary_color = models.CharField(max_length=7, blank=True)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    total_ties = models.IntegerField(default=0)
    last_seen = models.DateTimeField(default="2020-01-01 00:00")
    hasChallenge = models.CharField(max_length=200, null = True)

    @property
    def total_games_played(self):
        return self.total_wins + self.total_ties + self.total_losses

    @property
    def is_online(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        time_since_last_seen = now - self.last_seen
        
        # This threshold can be tuned
        threshold = datetime.timedelta(seconds=30)
        return time_since_last_seen <= threshold

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name


class GameObject(models.Model):
    # Board should be a JSON field which is a 2d list
    # This is a List[List[int]]
    # where 1 is player1, 2 is player2, and 0 is unset
    board = models.JSONField(null=True)
    # whoever starts the game will be player1
    player1: Profile = models.ForeignKey(
        Profile, on_delete=models.PROTECT, related_name="player1")
    player2: Profile = models.ForeignKey(
        Profile, on_delete=models.PROTECT, null=True, related_name="player2")
    # Colors will be a color value
    # https://stackoverflow.com/questions/8863810/python-find-similar-colors-best-way
    # will need to find if colors are too similar
    player1_color = models.CharField(max_length=7, null=True)
    player2_color = models.CharField(max_length=7, null=True)
    player1_entered = models.BooleanField(default=False)
    player2_entered = models.BooleanField(default=False)
    turn = models.ForeignKey(
        Profile, on_delete=models.PROTECT, related_name="turn", null=True)
    outcome = models.ForeignKey(
        Profile, on_delete=models.PROTECT, null=True, related_name="outcome")
    # Null when not started, False when in progress, True when over
    game_over = models.BooleanField(null=True)
    moves_played = models.IntegerField(default=0)
    timer = models.IntegerField(blank=True, default = 20)
    created_time = models.DateTimeField(auto_now=True)

class Chat(models.Model):
    input_text = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_time = models.DateTimeField(auto_now=True)
    game = models.ForeignKey(GameObject, on_delete=models.CASCADE)
