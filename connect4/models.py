from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile:
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    image = models.FileField(blank=True, upload_to="connect4/static/connect4/images")
    primary_color = models.CharField()
    secondary_color = models.CharField()
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    total_ties = models.IntegerField(default=0)

class GameObject:
    # Board should be a JSON field with
    board = models.JSONField()
    # whoever starts the game will be player1
    player1 = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="player1")
    player2 = models.ForeignKey(Profile, on_delete=models.PROTECT, null=True, related_name="player2")
    # Colors will be a color value selected from javascript
    player1_color = models.CharField()
    player2_color = models.CharField()
    turn = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="turn")
    outcome = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="outcome")
    # Null when not started, False when in progress, True when over
    game_over = models.BooleanField(null=True)
    moves_played = models.IntegerField(default=0)


