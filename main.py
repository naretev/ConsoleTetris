import os
import random
from pynput import keyboard

TICKRATE = 24
WIDTH = 10
HEIGHT = 22

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

class Game:
    def __init__(self):
        self.board = [[' ' for _ in range(WIDTH*2)] for _ in range(HEIGHT)]
        self.starting_coordinates = (2, 5)
        self.coordinates = self.starting_coordinates
        self.tick = 0
        self.over = False
        self.drop_rate = 24
        self.starting_rotation = 0
        self.rotation_index = 0
        self.piece_index = 0
        self.points = 0
    
    def increment(self):
        if self.tick % self.drop_rate == 0:
            self.move_piece('down')
        
        self.tick += 1
        self.tick %= TICKRATE

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
                    self.remove_lines()
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
        piece_index = random.randint(0, 6)

        self.piece_index = piece_index
        self.coordinates = self.starting_coordinates
        row, col = self.coordinates
        self.rotation_index = self.starting_rotation

        for row_mod, col_mod in PIECES[self.piece_index][self.rotation_index]:
            self.board[row+row_mod][(col+col_mod)*2] = '['
            self.board[row+row_mod][(col+col_mod)*2+1] = ']'
    

    def on_press(self, key: keyboard.Key | keyboard.KeyCode):
        if isinstance(key, keyboard.KeyCode):
            if key.char == 'q':
                self.over = True
            return

        if key.name == 'left':
            self.move_piece('left')
        if key.name == 'right':
            self.move_piece('right')
        if key.name == 'down':
            self.move_piece('down')
        if key.name == 'up':
            self.rotate_piece()
    
    def render(self):
        for i in range(2, len(self.board)):
            row = self.board[i]
            print('<', end='')
            for cell in row:
                print(cell, end='')
            print('>')
        print(' ' + 'v' * len(self.board[0]) + ' ' + 'points: ' + str(self.points))

    def remove_lines(self):
        points = 10
        for row in range(HEIGHT):
            if ' ' not in self.board[row]:
                points *= 2
                self.board = [[' '] * WIDTH*2] + self.board[:row] + self.board[row+1:]
        self.points += points

def main():
    game = Game()
    game.add_piece()

    while True:
        with keyboard.Listener(game.on_press) as listener:
            listener.join(1/TICKRATE)
        
        game.increment()
        os.system('clear')
        game.render()

        if game.over:
            break

main()
