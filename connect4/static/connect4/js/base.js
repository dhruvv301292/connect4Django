"use strict"

function getAllGames() {    
    $.ajax({
        url: "connect4/get-games",
        dataType : "json",
        success: updateArena,
        error: updateError
    });
}


function updateArena(response) {
    let Games = response['Games']    
    if (Array.isArray(Games)) {       
        updateGamesList(Games)
    } else if (Games.hasOwnProperty('error')) {
        displayError(Games.error)
    } else {
        displayError(Games)
    }
}

function updateError(xhr, status, error) {
    displayError('Status=' + xhr.status + ' (' + error + ')')
}

function displayError(message) {
    $("#error").html(message);
}

function updateGamesList(games) {
    $('#games-list').empty()
    let count = 1
    $(games).each(function() {
        let my_id = "id_game_item_" + this.id   
        if (document.getElementById(my_id) == null) {   
            let elem =  '<li id="id_game_item_' + this.id + '" style="list-style: none"><div class="row bg-dark rounded mb-2"><div class="col-1"><span class="pad-0" style="font-family: FuturaExtraBold; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: white;">'
            + count + '</span></div><div class="col-3" id="id_game_' + this.id + '_player1"><span class="pad-0" style="font-family: FuturaExtraBold; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: white">' 
            + this.p1_username + '</span></div><div class="col-1"><span class="pad-0" style="font-family: FuturaExtraBold; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color:#FF1E4E">VS</span></div><div class="col-3" id="id_game_' + this.id + 
            '_player2"><span class="pad-0" style="font-family: FuturaExtraBold; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: white">'+ ((this.p2_username == null) ? "" : this.p2_username) + '</span></div>' + getButton(this)   
            $("#games-list").append(elem)
        }
        count += 1
    })
    $("form").each(function() {        
        let inputElem = document.createElement('input');
        inputElem.type = 'hidden';
        inputElem.name = 'csrfmiddlewaretoken';
        inputElem.value = getCSRFToken();
        this.appendChild(inputElem);
     });
}

function getButton(game) {
    if (game.p2_username != null && myUserName == game.p1_username) {  
        let playgame = '/connect4/playgame/' + game.id;
        console.log(playgame);
        return '<div class="col-3" id="id_game_'+ game.id +'_start"><form id="id_game_'+game.id+'_start_form" method="POST" action="'+playgame+'"><button class="start-button mx-auto" id="id_game_' + game.id + '_start_button" type="submit">Start</button></form></div><div class="col-1 d-flex flex-wrap align-items-center" id="id_game_'
        + game.id +'_delete"><button onclick="deleteGame('+game.id+')" class="btn px-0 py-0 float-right"><span class="fa fa-times-circle fa-3x cross-button"></span></button></div></div></li>'
    } else if (game.p2_username == null && myUserName == game.p1_username) {
        return '<div class="col-3 d-flex flex-wrap align-items-center" id="id_game_'+ game.id +'_start"><span class="pad-0 mx-auto" style="font-family: FuturaItalic; text-transform:uppercase; font-size: 4vh; line-height: 4vh; color:#F9C10B">WAITING</span></div><div class="col-1 d-flex flex-wrap align-items-center" id="id_game_'
        + game.id +'_delete"><button onclick="deleteGame('+game.id+')" class="btn px-0 py-0 float-right"><span class="fa fa-times-circle fa-3x cross-button"></span></button></div></div></li>'
    } else if (game.p2_username == null && myUserName != game.p1_username) {
        return '<div class="col-3 d-flex flex-wrap align-items-center" id="id_game_'+ game.id +'_start"><button class="start-button mx-auto" id="id_join_button_'+ game.id + '" onClick="addPlayer(' + game.id + ')">Join</button></div></div></li>'
    } else if (game.p2_username == myUserName) {
        return '<div class="col-3 d-flex flex-wrap align-items-center" id="id_game_'+ game.id +'_start"><span class="pad-0 mx-auto" style="font-family: FuturaItalic; text-transform:uppercase; font-size: 4vh; line-height: 4vh; color:white">READY</span></div><div class="col-1 d-flex flex-wrap align-items-center" id="id_game_'
        + game.id +'_leave"><button onclick="leaveGame('+game.id+')" class="btn px-0 py-0 float-right"><span class="fa fa-sign-out-alt fa-flip-horizontal fa-3x cross-button"></span></button></div></div></li>'
    } else if (game.p1_username != myUserName && game.p2_username != myUserName) {
        return '<div class="col-3 d-flex flex-wrap align-items-center" id="id_game_'+ game.id +'_start"><button class="start-button mx-auto" id="id_spectate_button_'+ game.id + '">Spectate</button></div></div></li>'
    }
}

function addPlayer(gameID) {    
    displayError('');
    $.ajax({
        url: "connect4/add-player",
        type: "POST",
        data: "username="+myUserName+"&game_id="+gameID+"&csrfmiddlewaretoken="+getCSRFToken(),
        dataType : "json",
        success: updateArena,
        error: updateError
    });    
}

function leaveGame(gameID) { 
    displayError('');
    $.ajax({
        url: "connect4/leave-game",
        type: "POST",
        data: "username="+myUserName+"&game_id="+gameID+"&csrfmiddlewaretoken="+getCSRFToken(),
        dataType : "json",
        success: updateArena,
        error: updateError
    });    
}

function deleteGame(gameID) {    
    displayError('');
    $.ajax({
        url: "connect4/delete-game",
        type: "POST",
        data: "username="+myUserName+"&game_id="+gameID+"&csrfmiddlewaretoken="+getCSRFToken(),
        dataType : "json",
        success: updateArena,
        error: updateError
    });    
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown";
}  

