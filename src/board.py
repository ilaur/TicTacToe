from PIL import ImageTk
from tkinter import Button


class Board(object):
    """Board object represents the board data in the game"""


    def __init__(self) -> None:
        """Creates the board slots"""
        self.reset()


    def update(self, player: "Player", image: ImageTk, buttons: list[Button]) -> bool:
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