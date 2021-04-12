import enum
import json
from typing import Optional, List
from connect4.models import GameObject


class GameState(enum.Enum):
    PLAYER_1_WON = 1
    PLAYER_2_WON = 2
    DRAW = 3
    NOT_ENDED = 4


class Connect4Game:
    def __init__(self, game_model):
        self.board = game_model.board
        self.player1 = str(game_model.player1.user.id)
        self.player2 = str(game_model.player2.user.id)
        self.whose_turn = str(game_model.turn.user.id)
        self._game_obj = game_model


    @staticmethod
    def from_game_object(game_model: GameObject):
        # TODO: Construct an appropriate instance here
        game = Connect4Game(game_model)
        game._validate_state()
        return game

    def to_game_object(self) -> GameObject:
        game = self._game_obj
        game.board = self.board
        game.game_over = self.is_game_over
        game.moves_played += 1

        if self.whose_turn == self.player1:
            game.turn = game.player2
        else:
            game.turn = game.player1
        
        end_game_state = self.end_game_state
        if end_game_state == GameState.PLAYER_1_WON:
            game.outcome = game.player1
        if end_game_state == GameState.PLAYER_2_WON:
            game.outcome = game.player2
        if end_game_state == GameState.DRAW:
            game.outcome = None

        return game
        

    @property
    def is_game_over(self) -> bool:
        pass

    def drop_disk(self, player_id, column) -> None:
        print(self.board)
        player_id = str(player_id)
        column = int(column)
        # validate if correct player is playing
        if player_id != self.whose_turn:
            raise Connect4GameError(f"It is player_id={self.whose_turn} turn to play, but player_id={player_id} tried to play instead")
        # validate if column can have disk dropped in it

        
        if player_id == self.player1:
            token_no = 1
        elif player_id == self.player2:
            token_no = 2

        for i in range(7):
            if self.board[column][i] == 0:
                self.board[column][i] = token_no
                break
        else:
            raise Connect4GameError(f"Column {column} is already full")

    @property
    def end_game_state(self) -> GameState:
        pass

    def _validate_state(self):
        # TODO check board state
        # List[List[int]
        # Num columns and rows
        # Difference of 1 disk only bw players
        pass


class Connect4GameError(Exception):
    def __init__(self, message):
        self.message = message
