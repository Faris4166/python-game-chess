import pygame
import sys
import os

pygame.init()

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

WHITE = (245, 245, 220)
BLACK = (119, 148, 85)
SELECTED = (255, 0, 0)
MOVE_DOT = (0, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

font = pygame.font.SysFont(None, 48)

def resource_path(relative_path):
    """ หา path ที่ถูกต้องสำหรับ PyInstaller หรือ Python ปกติ """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_images():
    pieces = ['pawn','rook','knight','bishop','queen','king']
    images = {}
    for color in ['w','b']:
        for piece in pieces:
            img_path = resource_path(f"images/{color}_{piece}.png")
            img = pygame.image.load(img_path)
            img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
            images[f"{color}_{piece}"] = img
    return images

class Piece:
    def __init__(self, row, col, color, kind, images):
        self.row = row
        self.col = col
        self.color = color
        self.kind = kind
        self.images = images

    def draw(self, screen):
        x = self.col * SQUARE_SIZE
        y = self.row * SQUARE_SIZE
        key = ('w' if self.color == 'white' else 'b') + '_' + self.kind
        screen.blit(self.images[key], (x, y))

    def get_valid_moves(self, pieces):
        moves = []
        occupied = {(p.row, p.col): p for p in pieces}
        direction = -1 if self.color == 'white' else 1

        def is_enemy(r, c):
            return (r, c) in occupied and occupied[(r, c)].color != self.color

        def is_empty(r, c):
            return (r, c) not in occupied

        if self.kind == 'pawn':
            if 0 <= self.row + direction < 8:
                if is_empty(self.row + direction, self.col):
                    moves.append((self.row + direction, self.col))
                    start_row = 6 if self.color == 'white' else 1
                    if self.row == start_row and is_empty(self.row + 2 * direction, self.col):
                        moves.append((self.row + 2 * direction, self.col))
                for dc in [-1, 1]:
                    r, c = self.row + direction, self.col + dc
                    if 0 <= c < 8 and is_enemy(r, c):
                        moves.append((r, c))

        elif self.kind == 'rook':
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                for i in range(1, 8):
                    r = self.row + dr * i
                    c = self.col + dc * i
                    if 0 <= r < 8 and 0 <= c < 8:
                        if is_empty(r, c):
                            moves.append((r, c))
                        elif is_enemy(r, c):
                            moves.append((r, c))
                            break
                        else:
                            break

        elif self.kind == 'bishop':
            for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
                for i in range(1, 8):
                    r = self.row + dr * i
                    c = self.col + dc * i
                    if 0 <= r < 8 and 0 <= c < 8:
                        if is_empty(r, c):
                            moves.append((r, c))
                        elif is_enemy(r, c):
                            moves.append((r, c))
                            break
                        else:
                            break

        elif self.kind == 'queen':
            moves.extend(Piece(self.row, self.col, self.color, 'rook', self.images).get_valid_moves(pieces))
            moves.extend(Piece(self.row, self.col, self.color, 'bishop', self.images).get_valid_moves(pieces))

        elif self.kind == 'king':
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    r = self.row + dr
                    c = self.col + dc
                    if 0 <= r < 8 and 0 <= c < 8 and (is_empty(r, c) or is_enemy(r, c)):
                        moves.append((r, c))

        elif self.kind == 'knight':
            for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
                r = self.row + dr
                c = self.col + dc
                if 0 <= r < 8 and 0 <= c < 8 and (is_empty(r, c) or is_enemy(r, c)):
                    moves.append((r, c))

        return moves

def draw_board(selected=None):
    for r in range(ROWS):
        for c in range(COLS):
            color = WHITE if (r + c) % 2 == 0 else BLACK
            rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)
            if selected == (r, c):
                pygame.draw.rect(screen, SELECTED, rect, 4)

def highlight_moves(moves):
    for r, c in moves:
        x = c * SQUARE_SIZE + SQUARE_SIZE // 2
        y = r * SQUARE_SIZE + SQUARE_SIZE // 2
        pygame.draw.circle(screen, MOVE_DOT, (x, y), 10)

def get_piece_at(pieces, r, c):
    for p in pieces:
        if p.row == r and p.col == c:
            return p
    return None

def create_pieces(images):
    pieces = []
    back = ['rook','knight','bishop','queen','king','bishop','knight','rook']
    for c, kind in enumerate(back):
        pieces.append(Piece(0, c, 'black', kind, images))
        pieces.append(Piece(7, c, 'white', kind, images))
    for c in range(8):
        pieces.append(Piece(1, c, 'black', 'pawn', images))
        pieces.append(Piece(6, c, 'white', 'pawn', images))
    return pieces

def show_game_over(winner):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    text = font.render(f"{winner.capitalize()} wins!", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))

    btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50)
    pygame.draw.rect(screen, (100, 200, 100), btn)
    reset_text = font.render("Reset", True, (0, 0, 0))
    screen.blit(reset_text, reset_text.get_rect(center=btn.center))
    return btn

def main():
    clock = pygame.time.Clock()
    images = load_images()
    pieces = create_pieces(images)
    selected = None
    valid_moves = []
    turn = 'white'
    winner = None
    reset_button = None

    running = True
    while running:
        clock.tick(60)
        draw_board(selected and (selected.row, selected.col))
        highlight_moves(valid_moves)

        for p in pieces:
            p.draw(screen)

        if winner:
            reset_button = show_game_over(winner)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif winner and event.type == pygame.MOUSEBUTTONDOWN:
                if reset_button and reset_button.collidepoint(event.pos):
                    pieces = create_pieces(images)
                    selected = None
                    valid_moves = []
                    turn = 'white'
                    winner = None
                    reset_button = None

            elif not winner and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                r, c = my // SQUARE_SIZE, mx // SQUARE_SIZE
                clicked = get_piece_at(pieces, r, c)

                if selected:
                    if (r, c) in valid_moves:
                        target = get_piece_at(pieces, r, c)
                        if target:
                            if target.kind == 'king':
                                winner = turn
                            pieces.remove(target)
                        selected.row = r
                        selected.col = c
                        turn = 'black' if turn == 'white' else 'white'
                    selected = None
                    valid_moves = []
                else:
                    if clicked and clicked.color == turn:
                        selected = clicked
                        valid_moves = clicked.get_valid_moves(pieces)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
