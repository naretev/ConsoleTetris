import os
from pynput import keyboard

FRAMERATE = 30
WIDTH = 10
HEIGHT = 20

DIRECTIONS = {
    '<': (0, -1),
    '>': (0, 1),
    'v': (1, 0)
}

class Game:
    def __init__(self):
        self.board = [['.' for _ in range(WIDTH*2)] for _ in range(HEIGHT)]
        self.coordinates = [0, 0]
        self.tick = 0
        self.over = False
        self.drop_rate = 15
    
    def increment(self):
        if self.tick % self.drop_rate == 0:
            self.move_block('v')

        self.tick += 1
        self.tick %= 30

    def move_block(self, dir: str):
        board = self.board
        i, j = self.coordinates
        i_mod, j_mod = DIRECTIONS[dir]

        if i+i_mod >= HEIGHT or j+j_mod < 0 or j+j_mod >= WIDTH: return
        board[i][j*2] = '.'
        board[i][j*2+1] = '.'
        board[i+i_mod][(j+j_mod)*2] = '['
        board[i+i_mod][(j+j_mod)*2+1] = ']'
        self.coordinates = [i+i_mod, j+j_mod]

    def rotate_block(self):
        return
    
    def add_block(self):
        board = self.board
        i, j = self.coordinates

        board[i][j*2] = '['
        board[i][j*2+1] = ']'
    

    def on_press(self, key: keyboard.Key | keyboard.KeyCode):
        if isinstance(key, keyboard.KeyCode):
            if key.char == 'q': self.over = True
            return

        if key.name == 'left':
            self.move_block('<')
        if key.name == 'right':
            self.move_block('>')
        if key.name == 'down':
            self.move_block('v')
        if key.name == 'up':
            self.rotate_block()
    
    def print_board(self):
        board = self.board
        for row in board:
            print('<', end='')
            for cell in row:
                print(cell, end='')
            print('>')
        print(' ' + 'v' * len(board[0]) + ' ')


def main():
    game = Game()
    game.add_block()

    while True:
        with keyboard.Listener(game.on_press) as listener:
            listener.join(1/FRAMERATE)
        
        game.move_block('v')
        os.system('clear')
        game.print_board()

        if game.over:
            break

main()
