from enum import Enum


class PlayerType(Enum):
    ONE = 1
    TWO = 2


class Player(object):
    """Player objects represents a player data in the game"""


    def __init__(self, name: str, player_type: PlayerType) -> None:
        """Initialize the player data"""
        self.name = name
        self.player_type = player_type
        self.mark = "X" if player_type == PlayerType.ONE else "O"
        self.reset()


    def process_input(self) -> None:
        """Process the player input"""
        if 1 > self.position > 9:
            self.reset()
    

    def reset(self) -> None:
        """Resets the current player"""
        self.position = -1


class AIAgent(Player):
    """AI agent that can play against a regular player"""


    def __init__(self, board: "Board", name: str, player_type: PlayerType) -> None:
        """Initialize the AI agent"""
        super().__init__(name, player_type)
        self.game_board = board
        self.opponent_mark = "O" if self.mark == "X" else "X"

    
    def process_input(self) -> None:
        """Picks the most efficient postion using the minimax algorithm"""
        best_score = float("-inf")
        best_move = None

        for pos in self.game_board.get_available_positions():
            self.game_board.board[pos] = self.mark
            score = self.minimax(0, False)
            self.game_board.board[pos] = " "
            if score > best_score:
                best_score = score
                best_move = pos
        self.position = best_move


    def minimax(self, depth: int, is_maximazing: bool) -> int:
        """Maximize the score of all possibilities for the AI and minimize the score for the player"""
        winner = self.game_board.check_state()
        if winner == self.mark:
            return 1
        if winner == self.opponent_mark:
            return -1
        if self.game_board.is_full():
            return 0
        
        if is_maximazing:
            best_score = float("-inf")
            for pos in self.game_board.get_available_positions():
                self.game_board.board[pos] = self.mark
                score = self.minimax(depth + 1, False)
                self.game_board.board[pos] = " "
                best_score = max(score, best_score)
            return best_score
        else:
            best_score = float("inf")
            for pos in self.game_board.get_available_positions():
                self.game_board.board[pos] = self.opponent_mark
                score = self.minimax(depth + 1, True)
                self.game_board.board[pos] = " "
                best_score = min(score, best_score)
            return best_score