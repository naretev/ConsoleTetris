from datetime import datetime
from enum import Enum, auto
import os
import random
from time import sleep
from pynput import keyboard

class Direction(Enum):
    LEFT = (0, -1)
    RIGHT = (0, 1)
    DOWN = (1, 0)

class Rotation(Enum):
    CLOCKWISE = 1
    COUNTER_CLOCKWISE = -1

class Operation(Enum):
    ADD = auto()
    REMOVE = auto()

TICKRATE = 60
WIDTH = 10
HEIGHT = 22
SPAWN_COORDINATES = (2, 5)
SPAWN_ROTATION_INDEX = 0
DROP_RATES = [60, 30, 20, 15, 12, 10, 6, 5, 4, 3, 2, 1]
SCORE_PER_LINE_CLEARED = [0, 40, 100, 300, 1200]

T_PIECE_ROTATIONS = (
    ((0, -1), (0, 0), (0, 1), (1, 0)),
    ((-1, 0), (0, -1), (0, 0), (1, 0)),
    ((-1, 0), (0, -1), (0, 0), (0, 1)),
    ((-1, 0), (0, 0), (0, 1), (1, 0)),
)

J_PIECE_ROTATIONS = [
    ((0, -1), (0, 0), (0, 1), (1, 1)),
    ((-1, 0), (0, 0), (1, -1), (1, 0)),
    ((-1, -1), (0, -1), (0, 0), (0, 1)),
    ((-1, 0), (-1, 1), (0, 0), (1, 0)),
]

Z_PIECE_ROTATIONS = [
    ((0, -1), (0, 0), (1, 0), (1, 1)),
    ((-1, 1), (0, 0), (0, 1), (1, 0)),
]

O_PIECE_ROTATIONS = [
    ((0, -1), (0, 0), (1, -1), (1, 0))
]

S_PIECE_ROTATIONS = [
    ((0, 0), (0, 1), (1, -1), (1, 0)),
    ((-1, -1), (0, -1), (0, 0), (1, 0)),
]

L_PIECE_ROTATIONS = [
    ((0, -1), (0, 0), (0, 1), (1, -1)),
    ((-1, -1), (-1, 0), (0, 0), (1, 0)),
    ((-1, 1), (0, -1), (0, 0), (0, 1)),
    ((-1, 0), (0, 0), (1, 0), (1, 1)),
]

LINE_PIECE_ROTATIONS = [
    ((0, -2), (0, -1), (0, 0), (0, 1)),
    ((-2, 0), (-1, 0), (0, 0), (1, 0)),
]

PIECES = [
    T_PIECE_ROTATIONS,
    J_PIECE_ROTATIONS,
    Z_PIECE_ROTATIONS,
    O_PIECE_ROTATIONS,
    S_PIECE_ROTATIONS,
    L_PIECE_ROTATIONS,
    LINE_PIECE_ROTATIONS
]

class Game:
    def __init__(self, start_drop_rate):
        self.over = False
        self.__board = [[' '] * WIDTH*2 for _ in range(HEIGHT)]
        self.__coordinates = SPAWN_COORDINATES
        self.__rotation_index = SPAWN_ROTATION_INDEX
        self.__start_drop_rate = start_drop_rate
        self.__tick = 0
        self.__drop_rate_index = 0
        self.__lines_cleared = 0
        self.__piece_index = 0
        self.__next_piece_index = self.__get_next_piece_index()
        self.__points = 0
        self.__spawn_next_piece()
        self.__on_press_actions = {
            'x': lambda: self.__rotate_piece(Rotation.CLOCKWISE),
            'z': lambda: self.__rotate_piece(Rotation.COUNTER_CLOCKWISE),
            'q': lambda: setattr(self, "over", True),
            'left':  lambda: self.__move_piece(Direction.LEFT),
            'right': lambda: self.__move_piece(Direction.RIGHT),
            'down':  lambda: self.__move_piece(Direction.DOWN),
            'up':    lambda: self.__rotate_piece(Rotation.CLOCKWISE),
        }
    
    def increment(self):
        self.__tick = (self.__tick+1) % TICKRATE
        self.__drop_rate_index = max(self.__start_drop_rate, self.__lines_cleared//10)

        if self.__tick % DROP_RATES[self.__drop_rate_index] == 0:
            self.__move_piece(Direction.DOWN)
        
        self.__render()

    def on_press(self, key: keyboard.Key | keyboard.KeyCode):
        key_press = key.char if isinstance(key, keyboard.KeyCode) else key.name
        if key_press in self.__on_press_actions:
            self.__on_press_actions[key_press]()

    def __get_next_piece_index(self) -> int:
        return random.randint(0, 6)
    
    def __add_piece(self, coordinates: tuple[int, int] = None, rotation_index: int = None):
        if coordinates is None: coordinates = self.__coordinates
        if rotation_index is None: rotation_index = self.__rotation_index
        self.__add_or_remove_piece('add', coordinates, rotation_index)
    
    def __remove_piece(self):
        self.__add_or_remove_piece('remove', self.__coordinates, self.__rotation_index)
    
    def __add_or_remove_piece(self, operation: Operation, coordinates: tuple[int, int], rotation_index: int):
        for piece_coordinates in PIECES[self.__piece_index][rotation_index]:
            row, col = self.__add_coordinates(coordinates, piece_coordinates)
            self.__board[row][(col)*2] = '[' if operation == Operation.ADD else ' '
            self.__board[row][(col)*2+1] = ']' if operation == Operation.ADD else ' '
    
    def __piece_fits(self, coordinates: tuple[int, int] = None, rotation_index: int = None) -> bool:
        if coordinates is None: coordinates = self.__coordinates
        if rotation_index is None: rotation_index = self.__rotation_index

        for piece_coordinates in PIECES[self.__piece_index][rotation_index]:
            row, col = self.__add_coordinates(coordinates, piece_coordinates)

            if row >= HEIGHT or col < 0 or col >= WIDTH or self.__board[row][(col)*2] != ' ':
                return False

        return True
    
    def __add_coordinates(sef, coords1: tuple[int, int], coords2: tuple[int, int]) -> tuple[int, int]:
        return tuple(a+b for a, b in zip(coords1, coords2))
    
    def __move_piece(self, direction: Direction):
        self.__remove_piece()

        new_coordinates = self.__add_coordinates(self.__coordinates, direction.value)
        if self.__piece_fits(coordinates=new_coordinates):
            self.__add_piece(coordinates=new_coordinates)
            self.__coordinates = new_coordinates
        else:
            self.__add_piece()
            if direction is Direction.DOWN:
                self.__clear_lines()
                self.__spawn_next_piece()
    
    def __rotate_piece(self, rotation: Rotation):
        self.__remove_piece()

        rotations = len(PIECES[self.__piece_index])
        new_rotation_index = (self.__rotation_index+rotation.value) % rotations

        if self.__piece_fits(rotation_index=new_rotation_index):
            self.__add_piece(rotation_index=new_rotation_index)
            self.__rotation_index = new_rotation_index
        else:
            self.__add_piece()
    
    def __spawn_next_piece(self):
        self.__piece_index = self.__next_piece_index
        self.__next_piece_index = self.__get_next_piece_index()
        self.__coordinates = SPAWN_COORDINATES
        self.__rotation_index = SPAWN_ROTATION_INDEX

        if not self.__piece_fits():
            self.over = True

        self.__add_piece()
    
    def __render(self):
        print("\033[H", end="")
        for i in range(2, len(self.__board)):
            print('<', end='')
            for j in range(len(self.__board[0])):
                print(self.__board[i][j], end='')
            print('>', end='')

            if i in (8, 14):
                print('  ' + '#'*14, end='')
            if i == 9:
                print('  ' + '#', end='')
                print(' '*4 + 'NEXT' + ' '*4, end='')
                print('#', end='')
            if i in range(10, 14):
                print('  ' + '#', end='')
                row, col = 11, 3
                for k in range(6):
                    if any(row+row_mod == i and col+col_mod == k
                           for row_mod, col_mod in PIECES[self.__next_piece_index][SPAWN_ROTATION_INDEX]):
                        print('[]', end='')
                    else:
                        print('  ', end='')
                print('#', end='')

            print()
        print(' ' + 'v'*WIDTH*2 + ' '*3 + 'points: ' + str(self.__points) + ' lines cleared: ' + str(self.__lines_cleared))
    
    def __clear_lines(self):
        lines_cleared = 0
        for row in range(HEIGHT):
            if ' ' not in self.__board[row]:
                self.__board = [[' '] * WIDTH*2] + self.__board[:row] + self.__board[row+1:]
                lines_cleared += 1
        self.__points += SCORE_PER_LINE_CLEARED[lines_cleared]
        self.__lines_cleared += lines_cleared

def main():
    while True:
        start_drop_rate = -1
        while start_drop_rate not in range(12):
            start_drop_rate = int(input('Enter starting difficulty (1-12): '))-1

        game = Game(start_drop_rate)

        listener = keyboard.Listener(on_press=game.on_press)
        listener.start()

        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

        while not game.over:
            before = datetime.now().timestamp()

            game.increment()

            after = datetime.now().timestamp()
            time_elapsed = after-before
            sleep(max((1/TICKRATE)-time_elapsed, 0))
        
        listener.stop()
        print('GAME OVER')
        
        if input('Play again? (*/n):') == 'n':
            break

main()
