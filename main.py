from collections import deque
import curses
from enum import Enum, auto
import random
from time import monotonic, sleep

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
HEIGHT = 20
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
        self.board = [[False] * WIDTH for _ in range(HEIGHT+2)]
        self.next_piece_index = self.__get_next_piece_index()
        self.lines_cleared = 0
        self.points = 0
        self.stats = [0] * len(PIECES)
        self.__coordinates = SPAWN_COORDINATES
        self.__rotation_index = SPAWN_ROTATION_INDEX
        self.__start_drop_rate = start_drop_rate
        self.__tick = 0
        self.__drop_rate_index = 0
        self.__piece_index = 0
        self.__on_press_actions = {
            ord('x'): lambda: self.__rotate_piece(Rotation.CLOCKWISE),
            ord('z'): lambda: self.__rotate_piece(Rotation.COUNTER_CLOCKWISE),
            ord('q'): lambda: setattr(self, "over", True),
            curses.KEY_LEFT: lambda: self.__move_piece(Direction.LEFT),
            curses.KEY_RIGHT: lambda: self.__move_piece(Direction.RIGHT),
            curses.KEY_DOWN: lambda: self.__move_piece(Direction.DOWN),
            curses.KEY_UP: lambda: self.__rotate_piece(Rotation.CLOCKWISE),
        }
        self.__spawn_next_piece()
    
    def increment(self):
        self.__tick = (self.__tick+1) % TICKRATE
        self.__drop_rate_index = max(self.__start_drop_rate, self.lines_cleared//10)

        if self.__tick % DROP_RATES[self.__drop_rate_index] == 0:
            self.__move_piece(Direction.DOWN)

    def on_press(self, key: int):
        if key in self.__on_press_actions:
            self.__on_press_actions[key]()

    def __get_next_piece_index(self) -> int:
        return random.randint(0, 6)
    
    def __add_piece(self, coordinates: tuple[int, int] = None, rotation_index: int = None):
        if coordinates is None: coordinates = self.__coordinates
        if rotation_index is None: rotation_index = self.__rotation_index
        self.__add_or_remove_piece(Operation.ADD, coordinates, rotation_index)
    
    def __remove_piece(self):
        self.__add_or_remove_piece(Operation.REMOVE, self.__coordinates, self.__rotation_index)
    
    def __add_or_remove_piece(self, operation: Operation, coordinates: tuple[int, int], rotation_index: int):
        for offsets in PIECES[self.__piece_index][rotation_index]:
            row, col = self.__add_coordinates(coordinates, offsets)
            self.board[row][col] = operation == Operation.ADD
    
    def __piece_fits(self, coordinates: tuple[int, int] = None, rotation_index: int = None) -> bool:
        if coordinates is None: coordinates = self.__coordinates
        if rotation_index is None: rotation_index = self.__rotation_index

        for offsets in PIECES[self.__piece_index][rotation_index]:
            row, col = self.__add_coordinates(coordinates, offsets)

            if row >= HEIGHT+2 or col < 0 or col >= WIDTH or self.board[row][col]:
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
        self.__piece_index = self.next_piece_index
        self.next_piece_index = self.__get_next_piece_index()
        self.stats[self.__piece_index] += 1

        self.__coordinates = SPAWN_COORDINATES
        self.__rotation_index = SPAWN_ROTATION_INDEX

        if not self.__piece_fits():
            self.over = True

        self.__add_piece()
    
    def __clear_lines(self):
        lines_cleared = 0
        for row in range(HEIGHT+2):
            if all(self.board[row]):
                self.board = [[False] * WIDTH] + self.board[:row] + self.board[row+1:]
                lines_cleared += 1
        self.points += SCORE_PER_LINE_CLEARED[lines_cleared]
        self.lines_cleared += lines_cleared

def render_board(win: curses.window, board: list[list[bool]]):
    for y, row in enumerate(board[2:]):
        for x, val in enumerate(row):
            if val:
                win.addstr(y, x*2, '[]', 2)
            else:
                win.addstr(y, x*2, '  ', 2)
    
    win.refresh()

def render_preview(win: curses.window, next_piece_index: int):
    win.clear()
    win.border(*'#'*8)
    win.addnstr(1, 4, 'NEXT', 4)

    row = 3
    col = 3
    for rowOffset, colOffset in PIECES[next_piece_index][0]:
        win.addnstr(row+rowOffset, (col+colOffset)*2, '[]', 2)
    win.refresh()

def render_stats(win: curses.window, stats: list[int]):
    row = 3
    col = 3

    for piece_index, num in enumerate(stats):
        win.addnstr(row+piece_index*3, (col+3)*2, str(num), 3)
        for rowOffset, colOffset in PIECES[piece_index][0]:
            win.addstr(row+rowOffset+piece_index*3, (col+colOffset)*2, '[]', 2)

    win.refresh()

def render_score(win: curses.window, score: int):
    row = 3
    col = 3

    win.addnstr(row, col, str(score), 6)

    win.refresh()

def poll_input(stdscr: curses.window, queue: deque):
    while True:
        key = stdscr.getch()
        if key == -1:
            break
        queue.append(key)

def main(stdscr: curses.window, game: Game):
    stdscr.nodelay(True)

    stdscr.bkgd(1)
    stdscr.vline(0, 22, '<', HEIGHT)
    stdscr.refresh()

    stats_win = curses.newwin(24, 18, 0, 0)
    
    stats_win.bkgd(1)
    stats_win.border(*'#'*8)
    stats_win.addnstr(1, 4, 'STATISTICS', 10)

    preview_win = curses.newwin(7, 12, 4, 48)
    preview_win.bkgd(1)

    board_win = curses.newwin(HEIGHT+1, WIDTH*2+1, 0, 23)

    board_win.bkgd(1)
    board_win.vline(0, WIDTH*2, '>', HEIGHT)
    board_win.hline(HEIGHT, 0, 'v', WIDTH*2)

    score_win = curses.newwin(6, 12, 14, 48)
    
    score_win.bkgd(1)
    score_win.border(*'#'*8)
    score_win.addnstr(1, 4, 'SCORE', 5)

    input_queue = deque()

    while not game.over:
        before = monotonic()

        poll_input(stdscr, input_queue)

        while len(input_queue) > 0:
            game.on_press(input_queue.popleft())

        game.increment()
        render_preview(preview_win, game.next_piece_index)
        render_score(score_win, game.points)
        render_stats(stats_win, game.stats)
        render_board(board_win, game.board)

        after = monotonic()
        time_elapsed = after-before
        sleep(max((1/TICKRATE)-time_elapsed, 0))

while True:
    start_drop_rate = -1
    while start_drop_rate not in range(12):
        start_drop_rate = int(input('Enter starting difficulty (1-12): '))-1

    game = Game(start_drop_rate)

    curses.wrapper(lambda stdscr: main(stdscr, game))
    
    print('GAME OVER')
    print('Score: ' + str(game.points) + ' Lines cleared: ' + str(game.lines_cleared))
    
    if input('Play again? (*/n):') == 'n':
        break
