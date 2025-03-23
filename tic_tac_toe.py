from os import walk
from enum import Enum
from PIL import Image, ImageTk
from tkinter import Tk, Button
from tkinter.ttk import Label

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
MENU_X_PADDING = SCREEN_WIDTH // 2 - 50
MENU_Y_PADDING = 10
FONT = ("MS Sans Serif", 16, "normal")

class PlayerType(Enum):
    ONE = 1
    TWO = 2


class GameState(Enum):
    TURN_P1 = 1
    TURN_P2 = 2
    DRAW = 3


class GameModes(Enum):
    SINGLE_PLAYER = 1
    MULTIPLAYER = 2
    MAIN_MENU = 3
    EXIT = 4


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


class Board(object):
    """Board object represents the board data in the game"""


    def __init__(self) -> None:
        """Creates the board slots"""
        self.reset()


    def update(self, player: Player, image: ImageTk, buttons: list[Button]) -> bool:
        """Update the board based on player input"""
        if -1 < player.position < 9 and self.board[player.position] == " ":
            self.board[player.position] = player.mark
            buttons[player.position].config({"image": image})

            return True

        return False


    def reset(self) -> None:
        """Resets the current board"""
        self.board = 9 * [" "]


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


    def __init__(self, source_path: str, image_size: tuple[int], sprite_config: dict) -> None:
        """Initialize the game assets, accepts dict config with filename and array of images"""
        self.image_refs = {}
        for _, _, files in walk(source_path):
            for file in files:
                image_ref = Image.open(f"{source_path}/{file}")
                img = image_ref.resize(image_size, Image.Resampling.LANCZOS)
                for sprite in sprite_config[file]:
                    self.image_refs[sprite.get("name")] = ImageTk.PhotoImage(img.crop(sprite.get("coords")))


class TicTacToe(object):
    """TicTacToe object in charge of running the game"""


    def __init__(self) -> None:
        """Initialize the game state, board and players"""
        self.board = Board()
        self.game_mode = GameModes.MAIN_MENU

        self.window = Tk()
        self.window.title("Tic Tac Toe")
        self.window.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")

        assets_config = {
            "ttt_sprite.png": [
                {"name": "X", "coords": (615, 50, 750, 250)},
                {"name": "O", "coords": (615, 300, 750, 500)},
                {"name": "blk", "coords": (0, 0, 135, 200)}
            ]
        }
        
        self.assets_loader = AssetsLoader(source_path="./assets",
                                          image_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
                                          sprite_config=assets_config)

        self.render_based_on_mode()

        self.window.mainloop()


    def handle_click_input(self, position: int) -> None:
        """Handles the user input from the mouse button clicks"""
        if -1 < position < 9:
            player = self.player_one if self.current_turn == GameState.TURN_P1 else self.player_two
            player.position = position


    def run_game(self) -> None:
        """Runs and handles the game states"""
        self.current_turn = GameState.TURN_P1
        self.player_one.reset()
        self.player_two.reset()
        self.board.reset()
        self.buttons = 9 * [0]
        for index in range(9):
            button = Button(image=self.assets_loader.image_refs.get("blk"), 
                            command=lambda pos=index: self.handle_click_input(pos))
            button.grid(row=index // 3, column=index % 3)
            self.buttons[index] = button
        
        current_player = self.player_one if self.current_turn == GameState.TURN_P1 else self.player_two
        self.bottom_label = Label(master=self.window,
                            text=f"Turn: {current_player.name}",
                            justify="left", font=FONT)
        self.bottom_label.grid(row=3, column=0)

        result = self.board.check_state()
        while not result:
            current_player = self.player_one if self.current_turn == GameState.TURN_P1 else self.player_two
            self.bottom_label.config({"text": f"Turn: {current_player.name}"})
            current_player.process_input()
            mark = self.assets_loader.image_refs["X"] if self.current_turn == GameState.TURN_P1 else self.assets_loader.image_refs["O"]
            if self.board.update(current_player, mark, self.buttons):
                self.current_turn = GameState.TURN_P1 if self.current_turn == GameState.TURN_P2 else GameState.TURN_P2
                result = self.board.check_state()
            if result is None and self.board.is_full():
                self.current_turn = GameState.DRAW
                break

            self.window.update_idletasks()
            self.window.update()

        self.continue_button = Button(master=self.window, text="Continue", 
                                      command=lambda game_mode=GameModes.MAIN_MENU: self.set_game_mode(game_mode)
                                     )
        self.continue_button.grid(row=3, column=2)
        if self.current_turn == GameState.DRAW:
            self.bottom_label.config({"text": "It's a draw!"})
        elif self.current_turn == GameState.TURN_P1:
            self.bottom_label.config({"text": f"{self.player_two.name} won!"})
        elif self.current_turn == GameState.TURN_P2:
            self.bottom_label.config({"text": f"{self.player_one.name} won!"})


    def set_game_mode(self, game_mode: GameModes) -> None:
        """Sets the game mode"""
        # Cleanup
        if game_mode == GameModes.MAIN_MENU:
            for button in self.buttons:
                button.destroy()

            self.bottom_label.destroy()
            self.continue_button.destroy()
        else:
            self.single_player_btn.destroy()
            self.multiplayer_btn.destroy()
            self.exit_btn.destroy()

        self.game_mode = game_mode
        self.render_based_on_mode()

    
    def render_based_on_mode(self) -> None:
        """Renders on the screen based on the game mode"""
        if self.game_mode == GameModes.MAIN_MENU:
            self.single_player_btn = Button(master=self.window, text="Single Player", 
                                            command=lambda game_mode=GameModes.SINGLE_PLAYER: self.set_game_mode(game_mode),
                                            justify="center"
                                           )
            self.single_player_btn.grid(row=0, column=0, padx=MENU_X_PADDING, pady=MENU_Y_PADDING)
            self.multiplayer_btn = Button(master=self.window, text="Multiplayer", 
                                          command=lambda game_mode=GameModes.MULTIPLAYER: self.set_game_mode(game_mode),
                                          justify="center"
                                         )
            self.multiplayer_btn.grid(row=1, column=0, padx=MENU_X_PADDING, pady=MENU_Y_PADDING)
            self.exit_btn = Button(master=self.window, text="Exit", 
                                   command=lambda: self.window.quit(),
                                   justify="center"
                                  )
            self.exit_btn.grid(row=2, column=0, padx=MENU_X_PADDING, pady=MENU_Y_PADDING)
        elif self.game_mode == GameModes.SINGLE_PLAYER:
            self.player_one = Player("Player One", PlayerType.ONE)
            self.player_two = AIAgent(self.board, "Player Two", PlayerType.TWO)
            self.run_game()
        elif self.game_mode == GameModes.MULTIPLAYER:
            self.player_one = Player("Player One", PlayerType.ONE)
            self.player_two = Player("Player Two", PlayerType.TWO)
            self.run_game()
