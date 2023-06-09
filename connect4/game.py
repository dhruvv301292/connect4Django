import enum
import json
from typing import Optional, List
from connect4.models import GameObject


class GameState(enum.Enum):
    PLAYER_1_WON = 1
    PLAYER_2_WON = 2
    DRAW = 3
    NOT_ENDED = 4


class SlotType(enum.IntEnum):
    EMPTY = 0
    PLAYER1_DISC = 1
    PLAYER2_DISC = 2


class Connect4Game:
    BOARD_HEIGHT = 6
    BOARD_WIDTH = 7
    NUM_PLAYERS = 2
    MAX_MOVES = BOARD_HEIGHT * BOARD_WIDTH

    def __init__(self, game_model: GameObject):
        self._game_obj = game_model
        self.moves_played = int(game_model.moves_played)
        self.player1 = str(game_model.player1.user.id)
        self.player2 = str(game_model.player2.user.id)
        self.whose_turn = str(game_model.turn.user.id)
        self.outcome: GameState = None
        if not game_model.game_over:
            self.outcome = GameState.NOT_ENDED
        else:
            if game_model.outcome is None:
                self.outcome = GameState.DRAW
            elif game_model.outcome == game_model.player1:
                self.outcome = GameState.PLAYER_1_WON
            elif game_model.outcome == game_model.player2:
                self.outcome = GameState.PLAYER_2_WON
            else:
                raise Connect4GameError(f"Invalid outcome value in game_model: {game_model.outcome}", show_user_error=False)
        self.board = game_model.board
        self.player1_num_moves, self.player2_num_moves = Connect4Game.count_player_moves(self.board)

    @staticmethod
    def count_player_moves(board):
        player1_num_moves = 0
        player2_num_moves = 0
        for col in range(Connect4Game.BOARD_WIDTH):
            for row in range(Connect4Game.BOARD_HEIGHT):
                if board[col][row] == SlotType.PLAYER1_DISC:
                    player1_num_moves += 1
                elif board[col][row] == SlotType.PLAYER2_DISC:
                    player2_num_moves += 1
        return player1_num_moves, player2_num_moves

    @staticmethod
    def from_game_object(game_model: GameObject):
        # Construct an instance of Connect4Game from the game_model object
        game = Connect4Game(game_model)

        # Check that the game state is valid
        game._validate_state()

         # return a valid instance of Connect4Game
        return game

    def to_game_object(self) -> GameObject:
        # fetch the game object state that we got from db
        game = self._game_obj

        # update the game object state
        game.board = self.board

        if self.whose_turn == self.player1:
            game.turn = game.player1
        elif self.whose_turn == self.player2:
            game.turn = game.player2
        else:
            raise Connect4GameError("Unexpected player {self.whose_turn} for taking turn, must be one of {self.player1} or {self.player2}", show_user_error=False)

        game.moves_played = self.moves_played
        game.game_over = self.game_over
        
        if self.outcome == GameState.PLAYER_1_WON:
            game.outcome = game.player1
        if self.outcome == GameState.PLAYER_2_WON:
            game.outcome = game.player2
        if self.outcome == GameState.DRAW:
            game.outcome = None

        # return the updated game object state
        return game

    def drop_disc(self, player_id, column) -> None:
        player_id = str(player_id)
        column = int(column)

        # check if game has ended
        if self.outcome != GameState.NOT_ENDED:
            raise Connect4GameError("Game over!")

        # validate if correct player is playing
        if player_id != self.whose_turn:
            raise Connect4GameError(f"It is player_id={self.whose_turn}'s turn to play, but player_id={player_id} tried to play instead")
        
        # validate if column in a valid range
        if column < 0 or column >= Connect4Game.BOARD_WIDTH:
            raise Connect4GameError("Invalid column for dropping a disc")

        # validate if column can have disc dropped in it
        if int(self.board[column][-1]) != SlotType.EMPTY:
            raise Connect4GameError(f"Column {column} is full")
        
        # determine which players disc is being dropped
        if player_id == self.player1:
            disc = SlotType.PLAYER1_DISC
        elif player_id == self.player2:
            disc = SlotType.PLAYER2_DISC

        # drop player's disc in the column
        for i in range(Connect4Game.BOARD_HEIGHT):
            if self.board[column][i] == SlotType.EMPTY:
                self.board[column][i] = disc
                break
        else:
            raise Connect4GameError(f"Column {column} is already full")

        self.update_game_on_drop_disc()


    @property
    def game_over(self):
        return self.outcome != GameState.NOT_ENDED

        
    def update_game_on_drop_disc(self):
        # update total number of moves
        self.moves_played += 1

        # update move count for player and toggle player
        if self.whose_turn == self.player1:
            self.player1_num_moves += 1
            self.whose_turn = self.player2
        else:
            self.player2_num_moves += 1
            self.whose_turn = self.player1
        
        # update outcome
        self.outcome = self.end_game_state

    @property
    def end_game_state(self) -> GameState:
        # TODO Check if the board has reached an end state with a winner
        if self.four_connected(SlotType.PLAYER1_DISC):
            print("Player 1 wins")
            return GameState.PLAYER_1_WON
        if self.four_connected(SlotType.PLAYER2_DISC):
            print("Player 2 wins")
            return GameState.PLAYER_2_WON
        if self.moves_played == Connect4Game.MAX_MOVES:
            print("Draw")
            return GameState.DRAW

        return GameState.NOT_ENDED

    def _validate_state(self):
        # Board type should be List[List[int]
        if type(self.board) != list:
            raise Connect4GameError(f"Columns are not of type list", show_user_error=False)
        for column in self.board:
            if type(column) != list:
                raise Connect4GameError(f"Rows are not of type list", show_user_error=False)
            for row in column:
                if type(row) != int:
                    raise Connect4GameError(f"Board has non integer type value", show_user_error=False)

        # Check board has valid number of columns and rows
        if len(self.board) != Connect4Game.BOARD_WIDTH:
            raise Connect4GameError(f"Invalid number of columns in board, expected {Connect4Game.BOARD_WIDTH} got {len(self.board)}", show_user_error=False)
        for i, column in enumerate(self.board):
            if len(column) != Connect4Game.BOARD_HEIGHT:
                raise Connect4GameError(f"Invalid number of rows in column {i}, expected {Connect4Game.BOARD_HEIGHT} got {len(column)}", show_user_error=False)
       
        # Difference of moves between players should not exceed 1
        if abs(self.player1_num_moves - self.player2_num_moves) > 1:
            raise Connect4GameError(f"Difference between player move count greater than 1!\nPlayer1 made {self.player1_num_moves} moves, while Player2 made {self.player2_num_moves}", show_user_error=False)

    def four_connected(self, playerType):
        # horizontal check
        for i in range(self.BOARD_WIDTH):
            for j in range(self.BOARD_HEIGHT-3):
                if (self.board[i][j] == playerType and self.board[i][j+1] == playerType and self.board[i][j+2] == playerType and self.board[i][j+3] == playerType):
                    return True
        # vertical check
        for i in range(self.BOARD_HEIGHT):
            for j in range(self.BOARD_WIDTH-3):
                if (self.board[j][i] == playerType and self.board[j+1][i] == playerType and self.board[j+2][i] == playerType and self.board[j+3][i] == playerType):
                    return True
        # diagonal ascending
        for i in range(3, self.BOARD_WIDTH):
            for j in range(self.BOARD_HEIGHT-3):
                if (self.board[i][j] == playerType and self.board[i-1][j+1] == playerType and self.board[i-2][j+2] == playerType and self.board[i-3][j+3] == playerType):
                    return True
        # diagonal descending
        for i in range(3, self.BOARD_WIDTH):
            for j in range(3, self.BOARD_HEIGHT):
                if (self.board[i][j] == playerType and self.board[i-1][j-1] == playerType and self.board[i-2][j-2] == playerType and self.board[i-3][j-3] == playerType):
                    return True
        return False

class Connect4GameError(Exception):
    def __init__(self, message, show_user_error=True):
        self.message = message
        self.show_user_error = show_user_error
