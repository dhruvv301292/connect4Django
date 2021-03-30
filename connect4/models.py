from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    image = models.FileField(default='connect4/static/connect4/profile.jpg', upload_to="connect4/static/connect4/images")
    content_type = models.CharField(max_length=50, default='image/jpeg')
    primary_color = models.CharField(max_length=7)
    secondary_color = models.CharField(max_length=7)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    total_ties = models.IntegerField(default=0)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

class GameObject(models.Model):
    # Board should be a JSON field which is a 2d list
    board = models.JSONField()
    # whoever starts the game will be player1
    player1 = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="player1")
    player2 = models.ForeignKey(Profile, on_delete=models.PROTECT, null=True, related_name="player2")
    # Colors will be a color value selected from javascript
    player1_color = models.CharField(max_length=7)
    player2_color = models.CharField(max_length=7)
    turn = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="turn")
    outcome = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="outcome")
    # Null when not started, False when in progress, True when over
    game_over = models.BooleanField(null=True)
    moves_played = models.IntegerField(default=0)