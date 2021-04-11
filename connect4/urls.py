"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from connect4 import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    path('profile', views.profile_action, name='profile'),
    path('photo/<int:id>', views.get_photo, name='get_photo'),
    path('update_profile', views.update_profile, name='update_profile'),
    path('startentergame/<str:game_id>', views.start_enter_game, name='startgame'),    
    path('add-game', views.add_game, name='add-game'),
    path('get-games', views.get_games, name='get-games'),
    path('connect4/get-games', views.get_games, name='get-games'),
    path('add-player', views.add_player, name='add-player'),
    path('connect4/add-player', views.add_player, name='add-player'),
    path('delete-game', views.del_game, name='delete-game'),
    path('connect4/delete-game', views.del_game, name='delete-game'),
    path('leave-game', views.leave_game, name='leave-game'),
    path('connect4/leave-game', views.leave_game, name='leave-game'),
    path('get-game/<int:gameId>', views.get_game, name='get-game'),
    path('add-column/<int:gameId>/<int:column>', views.add_column, name='add-column'),
]
