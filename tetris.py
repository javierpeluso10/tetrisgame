import pygame
import random

pygame.init()

# Configuración de pantalla y colores
SCREEN_WIDTH, SCREEN_HEIGHT = 300, 600
BLOCK_SIZE = 30
PLAY_WIDTH, PLAY_HEIGHT = 10 * BLOCK_SIZE, 20 * BLOCK_SIZE
TOP_LEFT_X, TOP_LEFT_Y = (SCREEN_WIDTH - PLAY_WIDTH) // 2, SCREEN_HEIGHT - PLAY_HEIGHT

# Colores para las piezas
COLORS = [(255, 165, 0), (0, 255, 255), (255, 0, 0), (0, 0, 255), (0, 255, 0), (128, 0, 255), (255, 255, 255)]  #CAMBIAR COLORES 

# Figuras de Tetris
SHAPES = [
    # I
    [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],
    
    # T
    [[[1, 1, 1], [0, 1, 0]], [[1, 0], [1, 1], [1, 0]], 
    [[0, 1, 0], [1, 1, 1]], [[0, 1], [1, 1], [0, 1]]],
    
    # Z
    [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]],
    
    # S
    [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]],
    
    # O
    [[[1, 1], [1, 1]]],
    
    # L
    [[[1, 1, 1], [1, 0, 0]], [[1, 0], [1, 0], [1, 1]], 
    [[0, 0, 1], [1, 1, 1]], [[1, 1], [0, 1], [0, 1]]],
    
    # J
    [[[1, 1, 1], [0, 0, 1]], [[1, 1], [1, 0], [1, 0]], 
    [[1, 0, 0], [1, 1, 1]], [[0, 1], [0, 1], [1, 1]]]
]


class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.choice(COLORS)
        self.rotation = 0

def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def convert_shape_format(piece):
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    for y, row in enumerate(shape_format):
        for x, cell in enumerate(row):
            if cell == 1:
                positions.append((piece.x + x, piece.y + y))

    return positions

def valid_space(piece, grid):
    accepted_positions = [[(x, y) for x in range(10) if grid[y][x] == (0, 0, 0)] for y in range(20)]
    accepted_positions = [x for sub in accepted_positions for x in sub]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] >= 0:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Piece(5, 0, random.choice(SHAPES))

def draw_text_middle(text, size, color, surface):
    font = pygame.font.Font(None, size)
    label = font.render(text, 1, color)

    surface.blit(label, (
        TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2),
        TOP_LEFT_Y + PLAY_HEIGHT / 2 - (label.get_height() / 2)
    ))

def draw_grid(surface, grid):
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(surface, grid[y][x],
                             (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    # Dibujar líneas de la cuadrícula
    for y in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (TOP_LEFT_X, TOP_LEFT_Y + y * BLOCK_SIZE),
                         (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + y * BLOCK_SIZE))
        for x in range(len(grid[y])):
            pygame.draw.line(surface, (128, 128, 128), (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y),
                             (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))

def clear_rows(grid, locked):
    rows_to_clear = 0
    for y in range(len(grid)-1, -1, -1):
        row = grid[y]
        if (0, 0, 0) not in row:
            rows_to_clear += 1
            for x in range(len(row)):
                del locked[(x, y)]
            for pos in sorted(list(locked), key=lambda pos: pos[1])[::-1]:
                x, pos_y = pos
                if pos_y < y:
                    new_pos = (x, pos_y + 1)
                    locked[new_pos] = locked.pop(pos)

    return rows_to_clear

def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))
    draw_grid(surface, grid)
    draw_text_middle(f'Puntaje: {score}', 30, (255, 255, 255), surface)

def main():
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    score = 0
    fall_speed = 0.5

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # Velocidad de caída
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

        shape_pos = convert_shape_format(current_piece)

        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(screen, grid, score)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    draw_text_middle("Game-Over", 40, (255, 255, 255), screen)
    pygame.display.update()
    pygame.time.delay(2000)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris para Vicky')


main()

