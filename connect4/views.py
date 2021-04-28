import logging
logging.basicConfig(format="[%(asctime)s] [%(levelname)s] [%(funcName)s] %(message)s", level=logging.DEBUG)

import json
import datetime
from timeit import default_timer as timer

from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http.request import HttpRequest

from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render, get_object_or_404, Http404, HttpResponse

from connect4.models import *
from connect4.game import Connect4Game, Connect4GameError, GameState
from connect4.forms import LoginForm, RegisterForm, ProfileForm


def update_last_seen(func):
    """Decorator for updating the last seen of a player
    
        Decorate view functions that are also annotated with @login_required to update a profile's last seen value.
    """
    def wrapped(*args, **kwargs):
        overhead_start = timer()
        # Find an HttpRequest like object
        http_request = None
        for arg in args:
            if isinstance(arg, HttpRequest):
                http_request = arg
                break

        if http_request is None:
            for _, kwarg in kwargs.items():
                if isinstance(kwarg, HttpRequest):
                    http_request = kwarg
                    break

        if http_request and http_request.user.is_authenticated:
            last_seen = datetime.datetime.now(datetime.timezone.utc)
            logging.info(f"User '{http_request.user}' last seen at {last_seen}")
            user_id = http_request.user.id
            profile = Profile.objects.get(user_id=user_id)
            profile.last_seen = last_seen
            profile.save()
        
        overhead_end = timer()
        logging.debug(f"Overhead time for update_last_seen={overhead_end - overhead_start}s")

        # call the original function and return
        return func(*args, **kwargs)

    return wrapped



@login_required
@update_last_seen
def home(request):      
    return render(request, 'connect4/arena.html', {'prim_color': Profile.objects.get(user_id=request.user.id).primary_color})

# create new game in arena
@login_required
@update_last_seen
def add_game(request):
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=403)
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=404)
    board = [[0 for i in range(6)] for j in range(7)]

    Player1 = Profile.objects.get(user_id=request.user.id)
    new_game = GameObject(board=board, player1=Player1, player2=None, player1_color=Player1.primary_color,
                          player2_color='#00B0F0', outcome=None, game_over=None, moves_played=0,
                          created_time=datetime.datetime.now())
    new_game.save()
    return redirect('home')


@login_required
@update_last_seen
def challenge_opponent(request):
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=403)
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=404)
    board = [[0 for i in range(6)] for j in range(7)]
   
    Player1 = Profile.objects.get(user_id=request.user.id)
    Player2 = Profile.objects.get(user__username=request.POST["player_2_username"])
    new_game = GameObject(board=board, player1=Player1, player2=Player2, player1_color=Player1.primary_color,
                          player2_color=Player2.primary_color, outcome=None, game_over=None, moves_played=0,
                          created_time=datetime.datetime.now())
    Player2.hasChallenge = Player1.user.username
    Player2.save()
    new_game.save()
    return redirect('home')


@login_required
@update_last_seen
def profile_action(request):
    logging.debug("PROFILE ACTION")
    context = {}
    profile = Profile.objects.get(user_id=request.user.id)

    form = ProfileForm(instance=profile)

    context['form'] = form
    context['profile'] = profile
    context['prim_color'] = profile.primary_color
    return render(request, 'connect4/profile.html', context)


@login_required
@update_last_seen
def leaderboard_action(request):
    context = {}    
    return render(request, 'connect4/leaderboard.html', context)


@login_required
@ensure_csrf_cookie
def update_profile(request):
    context = {}
    profile = Profile.objects.get(user_id=request.user.id)
    form = ProfileForm(request.POST, request.FILES, instance=profile)        
    context['profile'] = profile
    if not form.is_valid():
        context['form'] = form
    else:
        profile.content_type = form.cleaned_data['image'].content_type
        profile.image = form.cleaned_data['image']        
        profile.primary_color = form.cleaned_data['primary_color']        
        profile.secondary_color = form.cleaned_data['secondary_color']
        profile.save()
        context['form'] = ProfileForm(instance=profile)
        context['profile'] = profile
        context['prim_color'] = profile.primary_color
    return render(request, 'connect4/profile.html', context)


@login_required
def get_photo(request, id):
    item = get_object_or_404(Profile, id=id)
    logging.info('Picture #{} fetched from db: {} (type={})'.format(
        id, item.image, type(item.image)))

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not item.image:
        raise Http404

    return HttpResponse(item.image, content_type=item.content_type)


def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{ "error": "' + message + '" }'
    return HttpResponse(response_json, content_type='application/json', status=status)


def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'connect4/login.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'connect4/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('home'))


def logout_action(request):   
    logout(request)    
    return redirect(reverse('login'))

def oauth_register(request):
    userid = request.user.id
    user_object = get_object_or_404(User, id=userid)
    try:
        profile_object = Profile.objects.get(user_id=userid)
    except:
        profile_object = None
    # test if user profile exists already:
    if user_object and profile_object:
        return redirect(reverse('home'))

    elif user_object:
        print(type(user_object))

        profile = Profile(user=user_object, content_type='image/jpeg')
        profile.save()
        return redirect(reverse('home'))
            
    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=request.user.username,
                                        email=request.user.email,
                                        first_name=request.user.first_name,
                                        last_name=request.user.last_name)
    new_user.save()

    profile = Profile(user=new_user, content_type='image/jpeg')
    profile.save()
    return redirect(reverse('home'))

def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'connect4/register.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form
    # Validates the form.
    if not form.is_valid():
        return render(request, 'connect4/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    profile = Profile(user=new_user, content_type='image/jpeg',
                      primary_color=form.cleaned_data['primary_color'],
                      secondary_color=form.cleaned_data['secondary_color'])
    profile.save()
    login(request, new_user)
    return redirect(reverse('home'))


@login_required
def start_enter_game(request, game_id):
    context = {'game_id': game_id}
    game = GameObject.objects.get(id = int(game_id))    
    if not game:
        return _my_json_error_response("This game does not exist, man!")          
    if request.user.username == game.player1.user.username:
        context['selfplayer'] = game.player1
        context['opponent'] = game.player2
        game.player1_entered = True
        game.save()
    elif request.user.username == game.player2.user.username:
        context['selfplayer'] = game.player2
        context['opponent'] = game.player1
        game.player2_entered = True
        game.save()
    if game.game_over == None and game.player1_entered == True and game.player2_entered == True: #check if game not started and if both players have entered the game
        game.game_over = False
        game.turn = game.player1
        game.timer = 20
        game.save()
    context['player1'] = game.player1
    context['player2'] = game.player2
    context['p1_color'] = game.player1_color
    context['p2_color'] = game.player2_color
    if request.user.username in [game.player1.user.username, game.player2.user.username]:
        return render(request, 'connect4/game.html', context)
    else:
        logging.info("Returning spectator view")
        return render(request, 'connect4/spectator.html', context)


# for updating arena view using ajax
@login_required
@update_last_seen
def get_games(request):
    Games = []
    for game in GameObject.objects.all():
        game_i = {
            'id': game.id,
            'p1_username': game.player1.user.username,
            'p1_fullname': game.player1.user.get_full_name(),
            'player1_color': game.player1_color,
            'player2_color': game.player2_color,
            'player1_stats': "WINS: {} | LOSSES: {}".format(game.player1.total_wins, game.player1.total_losses),
            'player1_entered': game.player1_entered,
            'game_over': game.game_over,
            'moves_played': game.moves_played,
            'outcome': get_outcome(game)
        }
        if game.turn != None:
            game_i['turn'] = game.turn.user.username
        if game.player2:
            game_i['p2_username'] = game.player2.user.username
            game_i['p2_fullname'] = game.player2.user.get_full_name()
            game_i['player2_entered'] = game.player2_entered
            game_i['player2_stats'] = "WINS: {} | LOSSES: {}".format(game.player2.total_wins, game.player2.total_losses)
        else:
            game_i['p2_username'] = None
        
        Games.append(game_i)
    response_json = {'Games': Games}
    return HttpResponse(json.dumps(response_json), content_type='application/json')


def get_outcome(game: GameObject):
    if game.outcome == game.player1:
        return 1
    if game.outcome == game.player2:
        return 2
    if game.game_over and game.outcome is None:
        return 3

    return 4


# TODO: Rename method and/or update comment
@login_required
@update_last_seen
def get_game(request, game_id):
    game = get_object_or_404(GameObject, id=game_id)
    if not game:
        raise Http404
    
    response_json = _game_to_dict(game)
    return HttpResponse(json.dumps(response_json), content_type='application/json')


@login_required
@update_last_seen
def poll_game(request):
    game_id = request.POST['game_id']
    game_model: GameObject = get_object_or_404(GameObject, id=game_id)
    if not game_model:
        raise Http404

    # timer logic
    if game_model.turn and game_model.game_over == False:
        if game_model.timer >= 2:
            if request.user.username == game_model.turn.user.username:
                game_model.timer = game_model.timer - 2
        else:
            logging.info(f"GAME OVER for {game_id}: RAN OUT OF TIME")
            game_model.timer = 0
            game_model.game_over = True
            if game_model.turn.user.username == game_model.player1.user.username:
                game_model.outcome = game_model.player2
            else:
                game_model.outcome = game_model.player1            
            update_player_stats(game_model)
        game_model.save()

    response_json = _game_to_dict(game_model)
    return HttpResponse(json.dumps(response_json), content_type='application/json')
@login_required
@ensure_csrf_cookie
def add_chat(request):
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=404)
    message = request.POST['message']
    playerid = request.POST['player_id']
    gameid = request.POST['game_id']

    user = get_object_or_404(User, id=playerid)
    print(message)
    game = get_object_or_404(GameObject, id=gameid)
    if not game or not user:
        raise Http404
    chat = Chat(input_text=message, game=game, user=user, created_time=datetime.datetime.now())
    chat.save()
    logging.debug(f"REQUEST: {request}")
    #return redirect(start_enter_game, game_id=gameid)
    return poll_game(request)


def update_player_stats(game_model: GameObject):    
    p1 = game_model.player1
    p2 = game_model.player2
    if game_model.outcome == game_model.player1:
        logging.info(f"[update_player_stats] [{game_model.id}] OUTCOME IS 1")
        p1.total_wins = p1.total_wins + 1        
        p2.total_losses = p2.total_losses + 1
    elif game_model.outcome == game_model.player2:
        logging.info(f"[update_player_stats] [{game_model.id}] OUTCOME IS 2")
        p2.total_wins += 1
        p1.total_losses += 1
    elif game_model.outcome is None:            
        p2.total_ties += 1
        p1.total_ties += 1    
    p1.save()
    p2.save()    



def _game_to_dict(game: GameObject):
    game_i = {}
    game_i['id'] = game.id
    game_i['p1_username'] = game.player1.user.username
    if game.player2:
        game_i['p2_username'] = game.player2.user.username
    else:
        game_i['p2_username'] = None
    game_i['player1_color'] = game.player1_color
    game_i['player2_color'] = game.player2_color    
    if game.turn:
        game_i['turn'] = game.turn.user.username
    if game.outcome == game.player1:
        game_i['outcome'] = 1
    elif game.outcome == game.player2:
        game_i['outcome'] = 2
    elif game.game_over and game.outcome is None:
        game_i['outcome'] = 3
    else:
        game_i['outcome'] = 4
    game_i['game_over'] = game.game_over
    game_i['moves_played'] = game.moves_played
    game_i['board'] = game.board
    game_i['timer'] = game.timer

    try:
        logging.debug(f"game.id={game.id}")
        logging.debug(f"Chat.objects.all()[0].game_id={Chat.objects.all()[0].game_id}")
        chatHistory = Chat.objects.filter(game_id=game.id).order_by('created_time')
    except:
        print("in except")
        chatHistory = []
    messages = []
    for message in chatHistory:
        message_i = {
            'username': message.user.username,
            'message': message.input_text,
            'message_id': message.id,
        }
        messages.append(message_i)
    game_i['messages'] = {'Messages': messages}

    return game_i


@login_required
@update_last_seen
def play_turn(request):
    play_turn_start = timer()
    game_id = request.POST['game_id']
    player_id = request.POST['player_id']
    column = request.POST['column']

    logging.info(f"[play_turn] Playing turn for game_id={game_id}, player_id={player_id} in column={column}")
    
    # get the GameObject for gameId
    game_model: GameObject = get_object_or_404(GameObject, id=game_id)
    if not game_model:
        raise Http404

    # TODO: check if playerId is the logged in user, else throw an error

    game: Connect4Game = Connect4Game.from_game_object(game_model)

    try:
        game.drop_disc(player_id, column)
    except Connect4GameError as e:
        logging.error(f"[play_turn] [{game_id}] [{player_id}] An error occurred when trying to play turn: {e.message}")
        if e.show_user_error:
            # raise client error to inform the user about why this turn could not be played
            return HttpResponse(reason=e.message, status=406)
        else:
            # raise server error to log the error that led to invalid state
            return HttpResponse(reason=e.message, status=500)
        
    # get the updated state after a successful disc drop
    updated_game_model: GameObject = game.to_game_object()
    updated_game_model.timer = 20
    updated_game_model.save()

    if game.game_over:
        update_player_stats(updated_game_model)

    ## dhruv: doing the saving in update_player_stats instead 
    # p1 = game_model.player1
    # p2 = game_model.player2 

    # # save this updated model to the db
    # # TODO(devika): Save all objects in a single transaction
    # updated_game_model.save()
    # p1.save()
    # p2.save()

    game_dict = _game_to_dict(updated_game_model)

    play_turn_end = timer()
    logging.debug(f"play_turn took {play_turn_end - play_turn_start}s")

    return HttpResponse(json.dumps(game_dict), content_type='application/json')


@login_required
def reset_stats(request):
    context = {}
    profile = Profile.objects.get(user_id=request.user.id)
    profile.total_wins = 0
    profile.total_losses = 0
    profile.total_ties = 0
    profile.save()
    form = ProfileForm(instance=profile)

    context['form'] = form
    context['profile'] = profile
    context['prim_color'] = profile.primary_color
    return render(request, 'connect4/profile.html', context)


@login_required
def forfeit_game(request):
    if request.method == 'POST':
        if 'game_identity' in request.POST:
            game = GameObject.objects.get(id=request.POST['game_identity'])
            if request.user.username == game.player1.user.username:
                game.game_over = True
                game.outcome = game.player2  
                update_player_stats(game) 
                game.save()             
                return redirect('home')
            elif request.user.username == game.player2.user.username:
                game.game_over = True
                game.outcome = game.player1
                update_player_stats(game)
                game.save()
                return redirect('home')

@login_required
def add_player(request):
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=404)

    if not 'username' in request.POST or not request.POST['username']:
        return _my_json_error_response("You must have a valid username")

    if not 'game_id' in request.POST or not request.POST['game_id'] or not isInt(request.POST['game_id']):
        return _my_json_error_response("This game does not exist, man!")

    game = GameObject.objects.get(id=request.POST['game_id'])
    if not game:
        return _my_json_error_response("This game does not exist, man!")

    player2_profile = Profile.objects.get(user__username=request.POST['username'])
    game.player2 = player2_profile
    if player2_profile.primary_color:
        game.player2_color = player2_profile.primary_color
    game.save()
    return get_games(request)


# delete game that you created
@login_required
def del_game(request):
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=404)

    if not 'username' in request.POST or not request.POST['username']:
        return _my_json_error_response("You must have a valid username")

    if not 'game_id' in request.POST or not request.POST['game_id'] or not isInt(request.POST['game_id']):
        return _my_json_error_response("This game does not exist, man!")

    game = GameObject.objects.get(id=request.POST['game_id'])
    if not game:
        print("Not chat")
        return _my_json_error_response("This game does not exist, man!")

    if request.user.username == game.player1.user.username or request.user.username == game.player2.user.username:
        Chat.objects.filter(game_id=request.POST['game_id']).delete()
        GameObject.objects.filter(id=request.POST['game_id']).delete()
    return get_games(request)


def isInt(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

# remove yourself from game you joined as second playerasz
@login_required
def leave_game(request):
    if request.method != 'POST':
        return _my_json_error_response(
            "You must use a POST request for this operation. The current method is {}".format(request.method),
            status=404)

    if not 'username' in request.POST or not request.POST['username']:
        return _my_json_error_response("You must have a valid username")

    if not 'game_id' in request.POST or not request.POST['game_id'] or not isInt(request.POST['game_id']):
        return _my_json_error_response("This game does not exist, man!")

    game = GameObject.objects.get(id=request.POST['game_id'])
    if not game:
        return _my_json_error_response("This game does not exist, man!")

    player2_profile = game.player2
    if player2_profile.user.username != request.user.username:
        return _my_json_error_response("You are not part of this game")
    game.player2 = None
    game.game_over = None
    game.save()
    return get_games(request)


@login_required
@update_last_seen
def get_leaderboard(request):
    players = []
    for player in Profile.objects.all().order_by('-total_wins'):
        win_ratio = 0
        if player.total_games_played > 0:
            win_ratio = player.total_wins / player.total_games_played
            win_ratio = float("{:.2f}".format(win_ratio))
        player_i = {
            'id': player.id,
            'username': player.user.username,
            'prim_color': player.primary_color,
            'wins': player.total_wins,
            'total_games_played': player.total_games_played,
            'win_ratio': win_ratio,
            'is_online': player.is_online
        }
        players.append(player_i)

    response_json = {'Players': players}

    return HttpResponse(json.dumps(response_json), content_type='application/json')

@login_required
def check_challenge(request):
    player = Profile.objects.get(user__username=request.user.username)    
    if player.hasChallenge == None:        
        response_json = {'challenger': None}
    else:                
        challenger = player.hasChallenge        
        response_json = {'challenger': challenger}
        player.hasChallenge = None
        player.save()
    return HttpResponse(json.dumps(response_json), content_type='application/json')

    