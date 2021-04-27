"use strict"

function getAllGames() {    
    $.ajax({
        url: "connect4/get-games",        
        dataType : "json",
        success: updateArena,
        error: updateError
    });
}

function getLeaderboard() {    
    $.ajax({
        url: "connect4/get-leaderboard",        
        dataType : "json",
        success: updateLeaderBoardPage,
        error: updateError
    });
}

function checkChallenge() {   
    console.log("CHECKING!") 
    $.ajax({
        url: "connect4/check-challenge",        
        dataType : "json",
        success: enablePopup,
        error: null
    });  
}


function updateLeaderBoardPage(response) {
    let players = response['Players']    
    if (Array.isArray(players)) {       
        updateLeaderboard(players)
    } else if (players.hasOwnProperty('error')) {
        displayError(players.error)
    } else {
        displayError(players)
    }
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}

/*

<div class="msg_history">
                        <div class="incoming_msg">
                            <div class="received_msg">
                                <div class="received_withd_msg">
                                    <span class="sender_name"> Dave </span>
                                    <p>Test which is a new approach to have all
                                        solutions</p>
                                </div>
                            </div>
                        </div>
                        <div class="outgoing_msg">
                            <div class="sent_msg">
                                <p>Test which is a new approach to have all
                                    solutions</p>
                            </div>
                        </div>
                            <div class="input-group type_msg">
                                <input type="text" class="form-control" id="message_input" placeholder="Type a message"/>
                                <button class="msg_send_btn" type="button"><i class="fa fa-paper-plane" aria-hidden="true" onclick=alert("Replace_with_submit")></i></button>
                            </div>
                    </div>
 */

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
    // displayError('Status=' + xhr.status + ' (' + error + ')')
    displayError(error)
}

function displayError(message) {
    if (message.length > 20 || message.length == 0) {                
        $('#id_turn_div').css("color", "white").removeClass(['bg-success', 'bg-timer']).addClass('bg-danger').addClass(['animated', 'tada']);
    } else {        
        $('#id_turn_div').css("color", "white").css("text-transform", "capitalize").removeClass(['bg-success', 'bg-timer']).addClass('bg-danger').addClass(['animated', 'tada']).text(message);
    }    
}

function updateGamesList(games) {
    $('#games-list').empty()
    let count = 1
    $(games).each(function() {
        let my_id = "id_game_item_" + this.id   
        if (document.getElementById(my_id) == null) {   
            // let borderString = ""
            // if (this.p1_username == myUserName) {
            //     borderString = "border-p1"
            // }
            let elem =  '<li id="id_game_item_' + this.id + '" style="list-style: none"><div class="row bg-dark rounded mb-2 border "><div class="col-1 d-flex flex-wrap align-items-center""><span class="pad-0" style="font-family: FuturaExtraBold; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: white;">'
            + count + '</span></div><div class="col-3 d-flex flex-wrap align-items-center"" id="id_game_' + this.id + '_player1"><span tabindex="0" data-toggle="popover" data-trigger="focus" data-placement="bottom" title="'+ this.p1_username +'" data-content="'+ this.player1_stats+ '"  class="pad-0" style="font-family: FuturaExtraBold; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: white">' 
            + this.p1_username + '</span></div><div class="col-1 d-flex flex-wrap align-items-center""><span class="pad-0" style="font-family: FuturaExtraBold; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color:#FF1E4E">VS</span></div><div class="col-3 d-flex flex-wrap align-items-center"" id="id_game_' + this.id + 
            '_player2"><span tabindex="0" data-toggle="popover" data-trigger="focus" data-placement="bottom" title="'+ this.p2_username +'" data-content="'+ this.player2_stats+ '" class="pad-0" style="font-family: FuturaExtraBold; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: white">'+ ((this.p2_username == null) ? "" : this.p2_username) + '</span></div>' + getButton(this)   
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
    
    // function to show popover stats for user.
    $(function () {
        $('[data-toggle="popover"]').popover({
            placement: 'bottom',
            delay: {
                "show": 100,
                "hide": 100
            }
        });
    
        $('[data-toggle="popover"]').click(function () {
    
            setTimeout(function () {
                $('.popover').fadeOut('slow');
            }, 4000);
    
        });    
    })
}

function updateLeaderboard(players) {
    $('#players-list').empty()
    let count = 1
    $(players).each(function() {
        let my_id = "id_player_item_" + this.id  
        let get_photo = "/connect4/photo/" + this.id 
        let elem = ""
        if (document.getElementById(my_id) == null) {
            if (this.username == myUserName) {
                elem =  '<li id="id_player_item_' + this.id + '" style="list-style: none"><div id="id_player_bg_'+ this.id +'" class="row rounded mb-2 border" style="background:'+ this.prim_color +'"><div class="col-1 d-flex flex-wrap align-items-center""><span id="id_player_rank_'+ this.id +'" class="pad-0" style="font-family: FuturaBoldItalic; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: white;">'
                + count + '</span></div><div class="col-3 d-flex flex-wrap align-items-center"><image class="pad-0 leader-image border border-leader-self" src="'+ get_photo + '" id="id_player_' + this.id + '_image"></div><div class="col-5 d-flex flex-wrap align-items-center"><span class="pad-0" id="id_player_' + this.id + '_username" style="font-family: FuturaExtraBold; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: white">' 
                + this.username + '</span></div><div class="col-2 d-flex flex-wrap align-items-center"><span class="pad-0"></span></div><div class="col-1 d-flex flex-wrap align-items-center"><span class="pad-0" id="id_player_' + this.id + '_wins" style="font-family: FuturaItalic; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: white">' 
                + this.wins + '</span></div></div></li>'
            } else {
                if (this.is_online) {  
                    let challengeGame = '/connect4/challenge';                                   
                    elem =  '<li id="id_player_item_' + this.id + '" style="list-style: none"><div id="id_player_bg_'+ this.id +'" class="row bg-light rounded mb-2 border "><div class="col-1 d-flex flex-wrap align-items-center""><span id="id_player_rank_'+ this.id +'" class="pad-0" style="font-family: FuturaBoldItalic; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: grey;">'
                    + count + '</span></div><div class="col-3 d-flex flex-wrap align-items-center"><image class="pad-0 leader-image border border-leader" src="'+ get_photo + '" id="id_player_' + this.id + '_image"></div><div class="col-5 d-flex flex-wrap align-items-center"><span class="pad-0" id="id_player_' + this.id + '_username" style="font-family: FuturaExtraBold; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: black">' 
                    + this.username + '</span></div><div class="col-2 d-flex flex-wrap align-items-center"><form id="id_'+this.id+'_challenge_form" method="POST" action="'+challengeGame+'"><input type="hidden" name="player_2_username" value="'+this.username+'"><button type="submit" class="start-button-black" id="id_challenge_button_'+ this.id + '">Challenge</button></div><div class="col-1 d-flex flex-wrap align-items-center"><span class="pad-0" id="id_player_' + this.id + '_wins" style="font-family: FuturaItalic; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: black">' 
                    + this.wins + '</span></div></div></li>'
                } else {
                    elem =  '<li id="id_player_item_' + this.id + '" style="list-style: none"><div id="id_player_bg_'+ this.id +'" class="row bg-light rounded mb-2 border "><div class="col-1 d-flex flex-wrap align-items-center""><span id="id_player_rank_'+ this.id +'" class="pad-0" style="font-family: FuturaBoldItalic; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: grey;">'
                    + count + '</span></div><div class="col-3 d-flex flex-wrap align-items-center"><image class="pad-0 leader-image border border-leader" src="'+ get_photo + '" id="id_player_' + this.id + '_image"></div><div class="col-5 d-flex flex-wrap align-items-center"><span class="pad-0" id="id_player_' + this.id + '_username" style="font-family: FuturaExtraBold; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: black">' 
                    + this.username + '</span></div><div class="col-2 d-flex flex-wrap align-items-center"><span class="pad-0"></span></div><div class="col-1 d-flex flex-wrap align-items-center"><span class="pad-0" id="id_player_' + this.id + '_wins" style="font-family: FuturaItalic; text-transform:uppercase; font-size: 7vh; line-height: 7vh; color: black">' 
                    + this.wins + '</span></div></div></li>'
                }
            }            
            $("#players-list").append(elem)
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
        if (game.game_over == null) {
            let startgame = '/connect4/startentergame/' + game.id;        
            return '<div class="col-3 d-flex flex-wrap align-items-center text-center" id="id_game_'+ game.id +'_start"><form id="id_game_'+game.id+'_start_form" method="POST" action="'+startgame+'"><button class="start-button mx-auto" id="id_game_' + game.id + '_start_button" type="submit">Start</button></form></div><div class="col-1 d-flex flex-wrap align-items-center" id="id_game_'
            + game.id +'_delete"><button onclick="deleteGame('+game.id+')" class="btn px-0 py-0 float-right"><span class="fa fa-times-circle fa-3x cross-button"></span></button></div></div></li>'
        } else if (game.game_over == false) {
            let entergame = '/connect4/startentergame/' + game.id;
            return '<div class="col-3 d-flex flex-wrap align-items-center text-center" id="id_game_'+ game.id +'_start"><form id="id_game_'+game.id+'_enter_form" method="POST" action="'+entergame+'"><button class="start-button" id="id_game_' + game.id + '_start_button" type="submit">Enter</button></form></div><div class="col-1 d-flex flex-wrap align-items-center" id="id_game_'
            + game.id +'_delete"></div></div></li>'
        } else {
            let result = "No Result";
            if (game.outcome == 1) {
                result = game.p1_username + " won!";
            } else if (game.outcome == 2) {
                result = game.p2_username + " won!";
            }
            return '<div class="col-3 d-flex flex-wrap align-items-center" id="id_game_'+ game.id +'_start"><span class="pad-0" style="font-family: FuturaItalic; text-transform:uppercase; font-size: 4vh; line-height: 4vh; color:#F9C10B">' + result + '</span></div><div class="col-1 d-flex flex-wrap align-items-center" id="id_game_'
            + game.id +'_delete"><button onclick="deleteGame('+game.id+')" class="btn px-0 py-0 float-right"><span class="fa fa-times-circle fa-3x cross-button"></span></button></div></div></li>'            
        }       
    } else if (game.p2_username == null && myUserName == game.p1_username) {
        return '<div class="col-3 d-flex flex-wrap align-items-center" id="id_game_'+ game.id +'_start"><span class="pad-0" style="font-family: FuturaItalic; text-transform:uppercase; font-size: 4vh; line-height: 4vh; color:#F9C10B">WAITING</span></div><div class="col-1 d-flex flex-wrap align-items-center" id="id_game_'
        + game.id +'_delete"><button onclick="deleteGame('+game.id+')" class="btn px-0 py-0 float-right"><span class="fa fa-times-circle fa-3x cross-button"></span></button></div></div></li>'
    } else if (game.p2_username == null && myUserName != game.p1_username) {
        return '<div class="col-3 d-flex flex-wrap align-items-center text-center" id="id_game_'+ game.id +'_start"><button class="start-button" id="id_join_button_'+ game.id + '" onClick="addPlayer(' + game.id + ')">Join</button></div></div></li>'
    } else if (game.p2_username == myUserName) {
        if (game.player1_entered == false) {
            return '<div class="col-3 d-flex flex-wrap align-items-center text-center" id="id_game_'+ game.id +'_start"><span class="pad-0" style="font-family: FuturaItalic; text-transform:uppercase; font-size: 4vh; line-height: 4vh; color:white">READY</span></div><div class="col-1 d-flex flex-wrap align-items-center" id="id_game_'
            + game.id +'_leave"><button onclick="leaveGame('+game.id+')" class="btn px-0 py-0 float-right"><span class="fa fa-sign-out-alt fa-flip-horizontal fa-3x cross-button"></span></button></div></div></li>'
        } else if (game.player1_entered == true && game.game_over != true) {
            let entergame = '/connect4/startentergame/' + game.id;
            return '<div class="col-3 d-flex flex-wrap align-items-center text-center" id="id_game_'+ game.id +'_start"><form class="pad-0" id="id_game_'+game.id+'_enter_form" method="POST" action="'+entergame+'"><button class="start-button mx-auto" id="id_game_' + game.id + '_start_button" type="submit">Enter</button></form></div></div></li>'
        } else if (game.game_over == true) {
            let result = "No Result";
            if (game.outcome == 1) {
                result = game.p1_username + " won!";
            } else if (game.outcome == 2) {
                result = game.p2_username + " won!";
            }
            return '<div class="col-3 d-flex flex-wrap align-items-center" id="id_game_'+ game.id +'_start"><span class="pad-0" style="font-family: FuturaItalic; text-transform:uppercase; font-size: 4vh; line-height: 4vh; color:#F9C10B">' + result + '</span></div><div class="col-1 d-flex flex-wrap align-items-center" id="id_game_'
            + game.id +'_delete"><button onclick="deleteGame('+game.id+')" class="btn px-0 py-0 float-right"><span class="fa fa-times-circle fa-3x cross-button"></span></button></div></div></li>'
        }    
    } else if (game.p1_username != myUserName && game.p2_username != null && game.p2_username != myUserName) {
        if (game.game_over == null) {
            return '<div class="col-3 d-flex flex-wrap align-items-center text-center" id="id_game_'+ game.id +'_start"><span class="pad-0" style="font-family: FuturaItalic; text-transform:uppercase; font-size: 4vh; line-height: 4vh; color:white">STARTING SOON</span></div></div></li>'            
        } else if (!game.game_over)  {
            let spectategame = '/connect4/startentergame/' + game.id;
            return '<div class="col-3 d-flex flex-wrap align-items-center text-center" id="id_game_'+ game.id +'_spectate"><form class="pad-0" id="id_game_'+game.id+'_spectate_form" method="POST" action="'+spectategame+'"><button class="start-button mx-auto" id="id_game_' + game.id + '_spectate_button" type="submit">Spectate</button></form></div></div></li>'
        } else {
            let result = "No Result";
            if (game.outcome == 1) {
                result = game.p1_username + " won!";
            } else if (game.outcome == 2) {
                result = game.p2_username + " won!";
            }
            return '<div class="col-3 d-flex flex-wrap align-items-center" id="id_game_'+ game.id +'_start"><span class="pad-0" style="font-family: FuturaItalic; text-transform:uppercase; font-size: 4vh; line-height: 4vh; color:#F9C10B">' + result + '</span></div></div></li>'            
        }            
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

function playTurn(gameId, playerId, column) {
    displayError('');
    $.ajax({
        url: "/connect4/play-turn",
        type: "POST",
        data: "player_id="+playerId+"&game_id="+gameId+"&column=" +column+ "&csrfmiddlewaretoken="+getCSRFToken(),
        dataType : "json",
        success: updateGameView,
        error: updateError
    });
}

function pollGame(gameId) {
    console.log("Polling game for " + gameId);
    $.ajax({
        url: "/connect4/poll-game",
        type: "POST",
        data: "username="+myUserName+"&game_id="+gameId+"&csrfmiddlewaretoken="+getCSRFToken(),
        dataType : "json",
        success: updateGameView,
        error: updateError
    }); 
}
function addChat(gameId, playerId){

    console.log("Adding chat: "+ $("#message_input_chat").val())
    var message = $("#message_input_chat").val()
    $("#message_input_chat").val("")
    $.ajax({
        url:"/connect4/add-chat",
        type:"POST",
        data:"&game_id="+gameId+"&player_id="+playerId+"&message="+message+"&csrfmiddlewaretoken="+getCSRFToken(),
        dataType:"json",
        success:updateGameView,
        error:updateError
    });
}
function updateChat(items){
    console.log("Current value:"+ $("#message_input_chat").val())
    const myNode = document.getElementById("chat_messages");
    myNode.textContent = '';
    const message_input = $("#message_input_chat").val();

    $(items).each(function(){
        if (this.username===myUserName){
                myNode.insertAdjacentHTML('beforeend', '<div class="outgoing_msg" id="outgoing_'+this.message_id+'"> <div class="sent_msg" id="sent_"'+this.message_id+'> <p>'+sanitize(this.message)+'</p> </div> </div>')
        }
        else{
                myNode.insertAdjacentHTML('beforeend','<div class="incoming_msg" id="incoming_'+this.message_id+'"><div class="received_msg" id="received_"'+this.message_id+'"><div class="received_withd_msg" id="received_msg_"'+this.message_id+'"><span class="sender_name" id="sender_name_'+this.message_id+'">'+sanitize(this.username)+'</span><p>'+sanitize(this.message)+'</p></div></div></div>')
        }
    })
    $("#message_input_chat").val(message_input)
}


function updateGameView(response) {
    console.log(response);
    /*
    * UPDATE CHAT VIEW
    *
    * */
    if (Array.isArray(response.messages.Messages)){
        console.log("Updating chat")
        const message_input = document.getElementById("message_input_chat")
        updateChat(response.messages.Messages, message_input.value)
    }
    else if (response.hasOwnProperty('error')){
        displayError(response.error)
    }
    else{
        displayError(response)
    }
    /*
     * REST OF GAME LOGIC
     *
     **/
    if (response.outcome == 1) {
        let outcome_string = player1 + " wins!";
        $('#id_modal_text').text(outcome_string);
        $("#id_result_modal").modal();
    } else if (response.outcome == 2) {
        let outcome_string = player2 + " wins!";
        $('#id_modal_text').text(outcome_string);
        $("#id_result_modal").modal();
    } else if (response.outcome == 3) {
        let outcome_string = "It's a tie!";
        $('#id_modal_text').text(outcome_string);
        $("#id_result_modal").modal();
    }
    $('#id_timer_div').empty().text(response.timer);
    if (myUserName === player1) {
        $('#id_player_image').removeClass(['border-p2', 'border-p1']).addClass('border-p1')
        $('#id_opponent_image').removeClass(['border-p2', 'border-p1']).addClass('border-p2')
        $('#id_player_username').removeClass(['p1bg', 'p2bg']).addClass('p1bg')
        $('#id_player_name').removeClass(['p1bg', 'p2bg']).addClass('p1bg')
        $('#id_opponent_username').removeClass(['p1bg', 'p2bg']).addClass('p2bg')
        $('#id_opponent_name').removeClass(['p1bg', 'p2bg']).addClass('p2bg')
        if (response.turn == null) {
            $( "i[id^='topdisc']" ).removeClass(['top-disc-p2', 'top-disc-p1', 'disc-disabled']).addClass('disc-disabled');
            let turn_string = "WAITING FOR P2";
            $('#id_turn_div').empty().text(turn_string).css("color", "black").css("font-size", "3.0vh").css("text-transform", "uppercase").removeClass(['bg-success', 'bg-timer', 'bg-danger', 'animated', 'tada']).addClass('bg-timer');            
        } else if (myUserName === response.turn) {
            $( "i[id^='topdisc']" ).removeClass(['top-disc-p2', 'top-disc-p1', 'disc-disabled']).addClass('top-disc-p1');
            $('#id_turn_div').empty().text("Your turn").css("color", "white").css("font-size", "3.3vh").css("text-transform", "uppercase").removeClass(['bg-success', 'bg-timer', 'bg-danger', 'animated', 'tada']).addClass('bg-success');
        } else {
            $( "i[id^='topdisc']" ).removeClass(['top-disc-p2', 'top-disc-p1', 'disc-disabled']).addClass('disc-disabled');
            let turn_string = (response.turn + "'S TURN").toUpperCase();
            $('#id_turn_div').empty().text(turn_string).css("color", "black").css("font-size", "3.0vh").css("text-transform", "uppercase").removeClass(['bg-success', 'bg-timer', 'bg-danger', 'animated', 'tada']).addClass('bg-timer');            
        }       
    } else if (myUserName === player2) {
        $('#id_player_image').removeClass(['border-p2', 'border-p1']).addClass('border-p2')
        $('#id_opponent_image').removeClass(['border-p2', 'border-p1']).addClass('border-p1')
        $('#id_player_username').removeClass(['p1bg', 'p2bg']).addClass('p2bg')
        $('#id_player_name').removeClass(['p1bg', 'p2bg']).addClass('p2bg')
        $('#id_opponent_username').removeClass(['p1bg', 'p2bg']).addClass('p1bg')
        $('#id_opponent_name').removeClass(['p1bg', 'p2bg']).addClass('p1bg')
        if (myUserName === response.turn) {
            $( "i[id^='topdisc']" ).removeClass(['top-disc-p2', 'top-disc-p1', 'disc-disabled']).addClass('top-disc-p2');
            $('#id_turn_div').empty().text("Your turn").css("color", "white").css("font-size", "3.3vh").css("text-transform", "uppercase").removeClass(['bg-success', 'bg-timer', 'bg-danger', 'animated', 'tada']).addClass('bg-success');            
        } else {
            $( "i[id^='topdisc']" ).removeClass(['top-disc-p2', 'top-disc-p1', 'disc-disabled']).addClass('disc-disabled');
            let turn_string = (response.turn + "'S TURN").toUpperCase();
            $('#id_turn_div').empty().text(turn_string).css("color", "black").css("font-size", "3.0vh").removeClass(['bg-success', 'bg-timer', 'bg-danger', 'animated', 'tada']).addClass('bg-timer');                        
        }
    } else {
        if (player1 === response.turn) {
            $("#id_spectator_p1").removeClass(['name-spectator-player1', 'name-spectator-player1-turn']).addClass('name-spectator-player1-turn');
            $("#id_spectator_p2").removeClass(['name-spectator-player2', 'name-spectator-player2-turn']).addClass('name-spectator-player2');
        } else if (player2 === response.turn) {
            $("#id_spectator_p1").removeClass(['name-spectator-player1', 'name-spectator-player1-turn']).addClass('name-spectator-player1');
            $("#id_spectator_p2").removeClass(['name-spectator-player2', 'name-spectator-player2-turn']).addClass('name-spectator-player2-turn');
        }
    }
    for (let col = 0; col < 7; col++) {
        for (let row = 0; row < 6; row++) {
            let discValue = response.board[col][row];
            let discClass = "board-disc";
            if (discValue === 1) {
                discClass = "filled-red-disc";
            }
            else if (discValue === 2) {
                discClass = "filled-blue-disc";
            } else {
                if (myUserName === player1 && myUserName === response.turn) {
                    discClass = "board-disc-p1";
                } else if (myUserName === player2 && myUserName === response.turn) {
                    discClass = "board-disc-p2";
                } else {
                    discClass = "disc-disabled";
                }
            }
            document.getElementById('disc_' + row.toString() + col.toString()).className = "fas fa-circle fa-4x mx-auto " + discClass+ " pad-0";            
        }
    }
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

function enablePopup(response) {  
    if (response['challenger'] != null) {
        $.bootstrapGrowl("You've been challenged by " + response['challenger'], {            
            offset: {from: "bottom", amount: 50}, 
            delay: 7500,
            allow_dismiss: true,
            stackup_spacing: 10				
        });
    }     
}

