from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone
from connect4.models import GameObject, Profile
from connect4.forms import LoginForm, RegisterForm, ProfileForm
from django.shortcuts import render, get_object_or_404, Http404, HttpResponse
import datetime
import json
from json import JSONEncoder
from django.views.decorators.csrf import ensure_csrf_cookie


# Create your views here.
# Create your views here.


@login_required
def home(request):
    return render(request, 'connect4/arena.html', {})

# create new game in arena
@login_required
def add_game(request):
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=403)
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=404)
    context = {'games': GameObject.objects.all()}
    board = [[0 for i in range(6)] for j in range(7)]
    # loop starting from bottom to top
    total_board = {}
    for i in range(len(board) - 1, -1, -1):
        total_board[str('row_' + str(i))] = board[i]
    response_json = json.dumps(total_board)

    Player1 = Profile.objects.get(user_id=request.user.id)
    new_game = GameObject(board=response_json, player1=Player1, player2=None, player1_color='#FF1E4E',
                          player2_color='#00B0F0', turn=Player1, outcome=None, game_over=None, moves_played=0,
                          created_time=datetime.datetime.now())
    new_game.save()
    return redirect('home')

@login_required
def profile_action(request):
    context = {}
    profile = Profile.objects.get(user_id=request.user.id)

    form = ProfileForm(instance=profile)

    context['form'] = form
    context['profile'] = profile
    return render(request, 'connect4/profile.html', context)


@login_required
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
    return render(request, 'connect4/profile.html', context)


@login_required
def get_photo(request, id):
    item = get_object_or_404(Profile, id=id)
    print("Fetched item")
    print('Picture #{} fetched from db: {} (type={})'.format(
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
    context = {}
    game = GameObject.objects.get(id = int(game_id))    
    if not game:
        return _my_json_error_response("This game does not exist, man!")
    if game.game_over == None:
        game.game_over = False
        game.save()
    if request.user.username == game.player1.user.username:
        context['selfplayer'] = game.player1
        context['opponent'] = game.player2
    elif request.user.username == game.player2.user.username:
        context['selfplayer'] = game.player2
        context['opponent'] = game.player1
    # other game elements are yet to be encoded
    return render(request, 'connect4/game.html', context)

# for updating arena view using ajax
@login_required
def get_games(request):
    Games = []
    for game in GameObject.objects.all():
        game_i = {}
        game_i['id'] = game.id
        game_i['p1_username'] = game.player1.user.username
        if game.player2:
            game_i['p2_username'] = game.player2.user.username
        else:
            game_i['p2_username'] = None
        game_i['player1_color'] = game.player1_color
        game_i['player2_color'] = game.player2_color
        game_i['turn'] = game.turn.user.username
        game_i['outcome'] = game.outcome
        game_i['game_over'] = game.game_over
        game_i['moves_played'] = game.moves_played
        Games.append(game_i)
    response_json = {'Games': Games}
    return HttpResponse(json.dumps(response_json), content_type='application/json')

# add yourself as second player to existing game
@login_required
def get_game(request, gameId):
    game = get_object_or_404(GameObject, id=gameId)
    if not game:
        raise Http404
    game_i = {}
    game_i['id'] = game.id
    game_i['p1_username'] = game.player1.user.username
    if game.player2:
        game_i['p2_username'] = game.player2.user.username
    else:
        game_i['p2_username'] = None
    game_i['player1_color'] = game.player1_color
    game_i['player2_color'] = game.player2_color
    game_i['turn'] = game.turn.user.username
    game_i['outcome'] = game.outcome
    game_i['game_over'] = game.game_over
    game_i['moves_played'] = game.moves_played

    response_json = game_i
    return HttpResponse(json.dumps(response_json), content_type='application/json')

@login_required
def add_column(request, gameId, column):
    #add_column(gameId, column)
    # return redirect('playgame_action', gameId=gameId)
    return redirect('playgame_action')
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
        return _my_json_error_response("This game does not exist, man!")

    if request.user.username == game.player1.user.username:
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
