import os
import random
from pynput import keyboard

TICKRATE = 24
WIDTH = 10
HEIGHT = 22
SPAWN_COORDINATES = (2, 5)
SPAWN_ROTATION_INDEX = 0

DIRECTIONS = {
    'left': (0, -1),
    'right': (0, 1),
    'down': (1, 0)
}

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

DROP_RATES = [24, 12, 8, 6, 4, 3, 2, 1]

class Game:
    def __init__(self):
        self.board = [[' '] * WIDTH*2 for _ in range(HEIGHT)]
        self.coordinates = SPAWN_COORDINATES
        self.rotation_index = SPAWN_ROTATION_INDEX
        self.tick = 0
        self.drop_rate_index = 0
        self.lines_cleared = 0
        self.piece_index = 0
        self.next_piece_index = self._get_next_piece_index()
        self.points = 0
        self.over = False
        self.add_piece()

    def _get_next_piece_index(self) -> int:
        return random.randint(0, 6)
    
    def increment(self):
        self.tick = (self.tick+1) % TICKRATE
        self.drop_rate_index = self.lines_cleared//2

        if self.tick % DROP_RATES[self.drop_rate_index] == 0:
            self.move_piece('down')

    def move_piece(self, direction: str):
        row, col = self.coordinates

        for row_mod, col_mod in PIECES[self.piece_index][self.rotation_index]:
            self.board[row+row_mod][(col+col_mod)*2] = ' '
            self.board[row+row_mod][(col+col_mod)*2+1] = ' '

        row_dir, col_dir = DIRECTIONS[direction]
        row += row_dir
        col += col_dir
        
        for row_mod, col_mod in PIECES[self.piece_index][self.rotation_index]:
            if (row+row_mod >= HEIGHT
                or col+col_mod < 0
                or col+col_mod >= WIDTH
                or self.board[row+row_mod][(col+col_mod)*2] != ' '):

                row -= row_dir
                col -= col_dir
                for row_mod, col_mod in PIECES[self.piece_index][self.rotation_index]:
                    self.board[row+row_mod][(col+col_mod)*2] = '['
                    self.board[row+row_mod][(col+col_mod)*2+1] = ']'
                
                if direction == 'down':
                    self.clear_lines()
                    self.add_piece()
                return
        
        for row_mod, col_mod in PIECES[self.piece_index][self.rotation_index]:
            self.board[row+row_mod][(col+col_mod)*2] = ' '
            self.board[row+row_mod][(col+col_mod)*2+1] = ' '

        for row_mod, col_mod in PIECES[self.piece_index][self.rotation_index]:
            self.board[row+row_mod][(col+col_mod)*2] = '['
            self.board[row+row_mod][(col+col_mod)*2+1] = ']'
        
        self.coordinates = (row, col)

    def rotate_piece(self):
        row, col = self.coordinates

        for row_mod, col_mod in PIECES[self.piece_index][self.rotation_index]:
            self.board[row+row_mod][(col+col_mod)*2] = ' '
            self.board[row+row_mod][(col+col_mod)*2+1] = ' '

        rotations = len(PIECES[self.piece_index])
        new_rotation = (self.rotation_index+1) % rotations

        for row_mod, col_mod in PIECES[self.piece_index][new_rotation]:
            if (row+row_mod >= HEIGHT
                or col+col_mod < 0
                or col+col_mod >= WIDTH
                or self.board[row+row_mod][(col+col_mod)*2] != ' '):
                
                for row_mod, col_mod in PIECES[self.piece_index][self.rotation_index]:
                    self.board[row+row_mod][(col+col_mod)*2] = '['
                    self.board[row+row_mod][(col+col_mod)*2+1] = ']'
                return

        for row_mod, col_mod in PIECES[self.piece_index][new_rotation]:
            self.board[row+row_mod][(col+col_mod)*2] = '['
            self.board[row+row_mod][(col+col_mod)*2+1] = ']'
        
        self.rotation_index = new_rotation
    
    def add_piece(self):
        self.piece_index = self.next_piece_index
        self.next_piece_index = self._get_next_piece_index()
        self.coordinates = SPAWN_COORDINATES
        row, col = self.coordinates
        self.rotation_index = SPAWN_ROTATION_INDEX

        for row_mod, col_mod in PIECES[self.piece_index][self.rotation_index]:
            if (row+row_mod >= HEIGHT
                or col+col_mod < 0
                or col+col_mod >= WIDTH
                or self.board[row+row_mod][(col+col_mod)*2] != ' '):
                self.over = True

        for row_mod, col_mod in PIECES[self.piece_index][self.rotation_index]:
            self.board[row+row_mod][(col+col_mod)*2] = '['
            self.board[row+row_mod][(col+col_mod)*2+1] = ']'
    

    def on_press(self, key: keyboard.Key | keyboard.KeyCode):
        if isinstance(key, keyboard.KeyCode):
            if key.char == 'q':
                self.over = True
            return

        if key.name in ('left', 'right', 'down'):
            self.move_piece(key.name)
        if key.name == 'up':
            self.rotate_piece()
    
    def render(self):
        for i in range(2, len(self.board)):
            print('<', end='')
            for j in range(len(self.board[0])):
                print(self.board[i][j], end='')
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
                           for row_mod, col_mod in PIECES[self.next_piece_index][SPAWN_ROTATION_INDEX]):
                        print('[]', end='')
                    else:
                        print('  ', end='')
                print('#', end='')

            print()
        print(' ' + 'v' * len(self.board[0]) + ' '*3 + 'points: ' + str(self.points) + ' lines cleared: ' + str(self.lines_cleared))

    def clear_lines(self):
        points = 0
        for row in range(HEIGHT):
            if ' ' not in self.board[row]:
                self.board = [[' '] * WIDTH*2] + self.board[:row] + self.board[row+1:]
                points *= 3
                points += 10
                self.lines_cleared += 1
        self.points += points

def main():
    game = Game()

    listener = keyboard.Listener(on_press=game.on_press)
    listener.start()

    while not game.over:
        listener.join(1/TICKRATE)

        game.increment()
        os.system('clear')
        game.render()
    
    print('GAME OVER')
    listener.stop()

main()
