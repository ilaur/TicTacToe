from os import walk
from enum import Enum
from PIL import Image, ImageTk
from tkinter import Canvas, Tk

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800


class PlayerType(Enum):
    ONE = 1
    TWO = 2


class GameState(Enum):
    TURN_P1 = 1
    TURN_P2 = 2
    DRAW = 3


class Player(object):
    """Player objects represents a player data in the game"""


    def __init__(self, name: str, player_type: PlayerType) -> None:
        """Initialize the player data"""
        self.name = name
        self.position = -1
        self.player_type = player_type
        self.mark = "X" if player_type == PlayerType.ONE else "O"


    def process_input(self) -> None:
        """Process the player input"""
        if 1 > self.position > 9:
            self.position = -1


class Board(object):
    """Board object represents the board data in the game"""


    def __init__(self) -> None:
        """Creates the board slots"""
        self.board = 9 * [" "]


    def update(self, player: Player) -> bool:
        """Update the board based on player input"""
        if -1 < player.position < 10 and self.board[player.position] == " ":
            self.board[player.position] = player.mark
            return True

        return False


    def debug_render(self) -> None:
        """Renders the board in the console"""
        for i in range(0, 9, 3):
            print(f" {self.board[i]} | {self.board[i+1]} | {self.board[i+2]}")
            if i < 6:
                print(11 * "-")

    
    def get_available_positions(self) -> list[int]:
        """Returns a list of available positions on the board"""
        return [i for i, mark in enumerate(self.board) if mark == " "]
    

    def is_full(self) -> bool:
        """Returns if the board is full otherwise false"""
        return " " not in self.board
    

    def check_state(self) -> str | None:
        """Checks the internal state of the board for a change"""
        for i in range(0, 9, 3):
            if self.board[i] == self.board[i+1] == self.board[i+2] != " ":
                return self.board[i]
        for i in range(3):
            if self.board[i] == self.board[i+3] == self.board[i+6] != " ":
                return self.board[i]

        if self.board[0] == self.board[4] == self.board[8] != " ":
            return self.board[0]
        if self.board[6] == self.board[4] == self.board[2] != " ":
            return self.board[6]

        return None


class AIAgent(Player):
    """AI agent that can play against a regular player"""


    def __init__(self, board: Board, name: str, player_type: PlayerType) -> None:
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


class AssetsLoader(object):
    """Preloads the game assets"""


    def __init__(self, source_path: str, image_size: tuple[int]) -> None:
        """Initialize the game assets"""
        #TODO: Refactor, make this class more generic in order to support multiple assets
        self.image_refs = {}
        for _, _, files in walk(source_path):
            image_ref = Image.open(f"{source_path}/{files[0]}")
            background = image_ref.resize(image_size, Image.Resampling.LANCZOS)
            self.image_refs["background"] = ImageTk.PhotoImage(background.crop((0, 0, 600, 800)))
            self.image_refs["X"] = ImageTk.PhotoImage(background.crop((615, 50, 750, 250)))
            self.image_refs["O"] = ImageTk.PhotoImage(background.crop((615, 300, 750, 480)))


class TicTacToe(object):
    """TicTacToe object in charge of running the game"""


    def __init__(self) -> None:
        """Initialize the game state, board and players"""
        self.board = Board()
        self.player_one = Player("Player One", PlayerType.ONE)
        self.player_two = AIAgent(self.board, "Player Two", PlayerType.TWO)
        self.current_turn = GameState.TURN_P1

        self.window = Tk()
        self.window.title("Tic Tac Toe")
        self.assets_loader = AssetsLoader("./assets", (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.canvas = Canvas(self.window, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, image=self.assets_loader.image_refs.get("background"))
        self.canvas.bind("<Button 1>", lambda ev: self.handle_click_input(ev.x, ev.y))

        self.run_game()


    def handle_click_input(self, x: int, y: int) -> None:
        """Handles the user input from the mouse button clicks"""
        # TODO: Refactor hardcoded values
        row = col = -1
        if 150 < x < 285:
            col = 0
        elif 310 < x < 450:
            col = 1
        elif 475 < x < 615:
            col = 2

        if 65 < y < 255:
            row = 0
        elif 290 < y < 500:
            row = 1
        elif 530 < y < 730:
            row = 2

        if -1 < row < 3 and -1 < col < 3:
            player = self.player_one if self.current_turn == GameState.TURN_P1 else self.player_two
            player.position = row * 3 + col
    

    def render_mark(self, position: int) -> None:
        """Render the new mark on the position picked by the player"""
        x = position // 3
        y = position % 3
        img_mark = self.assets_loader.image_refs["X"] if self.current_turn == GameState.TURN_P1 else self.assets_loader.image_refs["O"]

        # TODO: Refactor hardcoded values
        if x == 0 and y == 0:
            self.canvas.create_image(200, 150, image=img_mark)
        elif x== 0 and y == 1:
            self.canvas.create_image(380, 150, image=img_mark)
        elif x == 0 and y == 2:
            self.canvas.create_image(560, 150, image=img_mark)
        elif x == 1 and y == 0:
            self.canvas.create_image(200, 390, image=img_mark)
        elif x == 1 and y == 1:
            self.canvas.create_image(380, 390, image=img_mark)
        elif x == 1 and y == 2:
            self.canvas.create_image(560, 390, image=img_mark)
        elif x == 2 and y == 0:
            self.canvas.create_image(200, 630, image=img_mark)
        elif x == 2 and y == 1:
            self.canvas.create_image(380, 630, image=img_mark)
        elif x == 2 and y == 2:
            self.canvas.create_image(560, 630, image=img_mark)


    def run_game(self) -> None:
        """Runs and handles the game states"""
        result = self.board.check_state()
        while not result:
            current_player = self.player_one if self.current_turn == GameState.TURN_P1 else self.player_two
            current_player.process_input()
            if self.board.update(current_player):
                self.render_mark(current_player.position)
                self.current_turn = GameState.TURN_P1 if self.current_turn == GameState.TURN_P2 else GameState.TURN_P2
                result = self.board.check_state()
            if result is None and self.board.is_full():
                self.current_turn = GameState.DRAW
                break

            self.window.update_idletasks()
            self.window.update()

        if self.current_turn == GameState.DRAW:
            print("It's a draw!")
        elif self.current_turn == GameState.TURN_P1:
            print("Player Two won!")
        elif self.current_turn == GameState.TURN_P2:
            print("Player One won!")
        self.window.mainloop()
