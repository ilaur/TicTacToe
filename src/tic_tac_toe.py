from os import walk
from enum import Enum
from tkinter import Tk, Button as TkButton
from tkinter.ttk import Label, Button as TtkButton
from PIL import Image, ImageTk

from board import Board
from player import Player, AIAgent, PlayerType


SCREEN_WIDTH = 430
SCREEN_HEIGHT = 650
MENU_X_PADDING = SCREEN_WIDTH // 2 - 50
MENU_Y_PADDING = 10
FONT = ("MS Sans Serif", 16, "normal")


class GameState(Enum):
    """Enumeration of the game states"""
    TURN_P1 = 1
    TURN_P2 = 2
    DRAW = 3


class GameModes(Enum):
    """Enumeration of the game modes"""
    SINGLE_PLAYER = 1
    MULTIPLAYER = 2
    MAIN_MENU = 3


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
                    img_name = sprite.get("name")
                    self.image_refs[img_name] = ImageTk.PhotoImage(img.crop(sprite.get("coords")))


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
                {"name": "X", "coords": (300, 50, 430, 250)},
                {"name": "O", "coords": (300, 240, 430, 440)},
                {"name": "blk", "coords": (205, 450, 335, 650)}
            ]
        }

        self.assets_loader = AssetsLoader(source_path="../assets",
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
        self.buttons = 9 * [None]
        for index in range(9):
            button = TkButton(image=self.assets_loader.image_refs.get("blk"), 
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

        self.continue_button = TtkButton(master=self.window, text="Continue", 
                                         command=lambda game_mode=GameModes.MAIN_MENU: self.set_game_mode(game_mode))
        self.continue_button.grid(row=3, column=2)
        if self.current_turn == GameState.DRAW:
            self.bottom_label.config({"text": "It's a draw!"})
        elif self.current_turn == GameState.TURN_P1:
            self.bottom_label.config({"text": f"{self.player_two.name} won!"})
        elif self.current_turn == GameState.TURN_P2:
            self.bottom_label.config({"text": f"{self.player_one.name} won!"})


    def set_game_mode(self, game_mode: GameModes) -> None:
        """Sets the game mode"""
        # Cleanup rendered elements
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
            self.single_player_btn = TtkButton(master=self.window, text="Single Player", 
                                               command=lambda game_mode=GameModes.SINGLE_PLAYER: self.set_game_mode(game_mode))
            self.single_player_btn.grid(row=0, column=0, padx=MENU_X_PADDING, pady=MENU_Y_PADDING)
            self.multiplayer_btn = TtkButton(master=self.window, text="Multiplayer", 
                                             command=lambda game_mode=GameModes.MULTIPLAYER: self.set_game_mode(game_mode))
            self.multiplayer_btn.grid(row=1, column=0, padx=MENU_X_PADDING, pady=MENU_Y_PADDING)
            self.exit_btn = TtkButton(master=self.window, text="Exit", 
                                      command=lambda: self.window.quit())
            self.exit_btn.grid(row=2, column=0, padx=MENU_X_PADDING, pady=MENU_Y_PADDING)
        elif self.game_mode == GameModes.SINGLE_PLAYER:
            self.player_one = Player("Player", PlayerType.ONE)
            self.player_two = AIAgent(self.board, "Computer", PlayerType.TWO)
            self.run_game()
        elif self.game_mode == GameModes.MULTIPLAYER:
            self.player_one = Player("Player One", PlayerType.ONE)
            self.player_two = Player("Player Two", PlayerType.TWO)
            self.run_game()
