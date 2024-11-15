import pygame
import random

pygame.init()

# Configuración de pantalla y colores
ANCHO_PANTALLA, ALTURA_PANTALLA = 600, 600
TAMANO_BLOQUE = 30
ANCHO_DE_JUEGO, ALTO_DE_JUEGO = 10 * TAMANO_BLOQUE, 20 * TAMANO_BLOQUE
TOP_LEFT_X, TOP_LEFT_Y = (ANCHO_PANTALLA - ANCHO_DE_JUEGO) // 2, ALTURA_PANTALLA - ALTO_DE_JUEGO

# Colores para las piezas
COLORES = [(255, 165, 0), (0, 255, 255), (255, 0, 0), (0, 0, 255), (0, 255, 0), (128, 0, 255), (255, 255, 255)]  #CAMBIAR COLORES 

# Figuras de Tetris
PIEZAS = [
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
        self.color = random.choice(COLORES)
        self.rotation = 0

def crear_grilla(posiciones_bloqueadas={}):
    grilla = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for y in range(len(grilla)):
        for x in range(len(grilla[y])):
            if (x, y) in posiciones_bloqueadas:
                grilla[y][x] = posiciones_bloqueadas[(x, y)]
    return grilla

def celdas_ocupadas_en_tablero(pieza):
    posiciones = []
    shape_format = pieza.shape[pieza.rotation % len(pieza.shape)]

    for y, row in enumerate(shape_format):
        for x, cell in enumerate(row):
            if cell == 1:
                posiciones.append((pieza.x + x, pieza.y + y))

    return posiciones

#verifica si una pieza puede colocarse en el tablero sin que choque con otras piezas ni salga de los límites
def espacio_valido_para_pieza(pieza, grilla):
    posicion_valida = [[(x, y) for x in range(10) if grilla[y][x] == (0, 0, 0)] for y in range(20)]
    posicion_valida = [x for sub in posicion_valida for x in sub]

    formatted = celdas_ocupadas_en_tablero(pieza)

    for pos in formatted:
        if pos not in posicion_valida:
            if pos[1] >= 0:
                return False
    return True

def chequear_game_over(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def generar_nueva_pieza():
    return Piece(5, 0, random.choice(PIEZAS))

def generar_texto_puntaje(text, size, color, surface):
    font = pygame.font.Font(None, size)
    label = font.render(text, 1, color)

    surface.blit(label, (
        TOP_LEFT_X + ANCHO_DE_JUEGO / 2 - (label.get_width() / 2),
        TOP_LEFT_Y + ALTO_DE_JUEGO / 2 - (label.get_height() / 2)
    ))

def dibujar_grilla(superficie, grilla):
    for y in range(len(grilla)):
        for x in range(len(grilla[y])):
            if grilla[y][x] != (0, 0, 0):  # Solo dibuja si hay un bloque
                bloque = pygame.Surface((TAMANO_BLOQUE, TAMANO_BLOQUE), pygame.SRCALPHA)  # Superficie con canal alfa
                bloque.fill((*grilla[y][x], 150))  # Añadir opacidad (0-255, donde 255 es opaco)
                superficie.blit(bloque, (TOP_LEFT_X + x * TAMANO_BLOQUE, TOP_LEFT_Y + y * TAMANO_BLOQUE))

    # Dibujar líneas de la cuadrícula
    for y in range(len(grilla)):
        pygame.draw.line(superficie, (128, 128, 128), (TOP_LEFT_X, TOP_LEFT_Y + y * TAMANO_BLOQUE),
                         (TOP_LEFT_X + ANCHO_DE_JUEGO, TOP_LEFT_Y + y * TAMANO_BLOQUE))
        for x in range(len(grilla[y])):
            pygame.draw.line(superficie, (128, 128, 128), (TOP_LEFT_X + x * TAMANO_BLOQUE, TOP_LEFT_Y),
                             (TOP_LEFT_X + x * TAMANO_BLOQUE, TOP_LEFT_Y + ALTO_DE_JUEGO))


def eliminar_linea_completa(grilla, locked):
    lineas_a_eliminar = 0
    for y in range(len(grilla)-1, -1, -1):  # Iterar desde abajo hacia arriba
        linea = grilla[y]
        if (0, 0, 0) not in linea:  # Si no hay bloques vacíos en la fila
            lineas_a_eliminar += 1
            # Eliminar las posiciones de la fila completa en `locked`
            for x in range(len(linea)):
                if (x, y) in locked:  # Verificar antes de eliminar
                    del locked[(x, y)]
            # Mover las filas superiores hacia abajo
            for pos in sorted(list(locked.keys()), key=lambda pos: pos[1], reverse=True):
                x, pos_y = pos
                if pos_y < y:  # Solo mover las filas por encima de la eliminada
                    nueva_posicion = (x, pos_y + 1)
                    locked[nueva_posicion] = locked.pop(pos)
    return lineas_a_eliminar

def renderizar_ventana_de_juego(superficie, grilla, puntaje=0, proxima_pieza=None):
    superficie.blit(fondo, (0, 0))  # Fondo primero
    dibujar_grilla(superficie, grilla)  # Luego cuadrícula
    generar_texto_puntaje(f'Puntaje: {puntaje}', 30, (255, 255, 255), superficie)
    dibujar_proxima_pieza(superficie, proxima_pieza)  # Dibujar la próxima pieza

def dibujar_proxima_pieza(superficie, pieza):
    # Tamaño de la zona para la próxima pieza
    x_offset = 450  
    y_offset = 20  

    # Obtenemos la forma de la próxima pieza
    shape_format = pieza.shape[pieza.rotation % len(pieza.shape)]
    
    # Dibujamos la próxima pieza
    for y, row in enumerate(shape_format):
        for x, cell in enumerate(row):
            if cell == 1:
                pygame.draw.rect(superficie, pieza.color,
                                 (x_offset + x * TAMANO_BLOQUE, y_offset + y * TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE))

    # Dibujar un borde para la sección de la próxima pieza
    pygame.draw.rect(superficie, (255, 255, 255), (x_offset - 5, y_offset - 5, 4 * TAMANO_BLOQUE + 10, 4 * TAMANO_BLOQUE + 10), 2)

def iniciar_juego():
    posiciones_bloqueadas = {}
    grilla = crear_grilla(posiciones_bloqueadas)
    cambio_de_pieza = False
    run = True
    pieza_actual = generar_nueva_pieza()
    pieza_siguiente = generar_nueva_pieza()  # La pieza siguiente
    reloj = pygame.time.Clock()
    tiempo_de_caida_de_pieza = 0
    puntaje = 0
    velocidad_de_caida_de_pieza = 0.5

    while run:
        grilla = crear_grilla(posiciones_bloqueadas)
        tiempo_de_caida_de_pieza += reloj.get_rawtime()
        reloj.tick()

        # Velocidad de caída
        if tiempo_de_caida_de_pieza / 1000 >= velocidad_de_caida_de_pieza:
            tiempo_de_caida_de_pieza = 0
            pieza_actual.y += 1
            if not espacio_valido_para_pieza(pieza_actual, grilla) and pieza_actual.y > 0:
                pieza_actual.y -= 1
                cambio_de_pieza = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pieza_actual.x -= 1
                if not espacio_valido_para_pieza(pieza_actual, grilla):
                        pieza_actual.x += 1
                if event.key == pygame.K_RIGHT:
                    pieza_actual.x += 1
                    if not espacio_valido_para_pieza(pieza_actual, grilla):
                        pieza_actual.x -= 1
                if event.key == pygame.K_DOWN:
                    pieza_actual.y += 1
                    if not espacio_valido_para_pieza(pieza_actual, grilla):
                        pieza_actual.y -= 1
                if event.key == pygame.K_UP:
                    pieza_actual.rotation = (pieza_actual.rotation + 1) % len(pieza_actual.shape)
                    if not espacio_valido_para_pieza(pieza_actual, grilla):
                        pieza_actual.rotation = (pieza_actual.rotation - 1) % len(pieza_actual.shape)

        shape_pos = celdas_ocupadas_en_tablero(pieza_actual)

        for x, y in shape_pos:
            if y > -1:
                grilla[y][x] = pieza_actual.color

        if cambio_de_pieza:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                posiciones_bloqueadas[p] = pieza_actual.color
            pieza_actual = pieza_siguiente
            pieza_siguiente = generar_nueva_pieza()  # Generar una nueva pieza
            cambio_de_pieza = False
            puntaje += eliminar_linea_completa(grilla, posiciones_bloqueadas) * 10

        renderizar_ventana_de_juego(pantalla, grilla, puntaje, pieza_siguiente)  # Pasar la próxima pieza
        pygame.display.update()

        if chequear_game_over(posiciones_bloqueadas):
            run = False

    generar_texto_puntaje("Game-Over", 40, (255, 255, 255), pantalla)
    pygame.display.update()
    pygame.time.delay(2000)

pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTURA_PANTALLA))
pygame.display.set_caption('Tetris para Vicky')


fondo = pygame.image.load('C:/Users/Javier Peluso/Desktop/tetrisgame/img/mi_imagen.jpg')  # Reemplaza 'tu_imagen.jpg' por el nombre de tu archivo
fondo = pygame.transform.scale(fondo, (ANCHO_PANTALLA, ALTURA_PANTALLA))

iniciar_juego()



