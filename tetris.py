import pygame
import random
import sys
import os 

pygame.init()

#RUTAS MULTIMEDIA
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_IMAGEN = os.path.join(BASE_DIR, 'img', 'mi_imagen.jpg')
RUTA_ROTATE_SOUND = os.path.join(BASE_DIR, 'sounds', 'rotate.wav')
RUTA_CLEAR_SOUND = os.path.join(BASE_DIR, 'sounds', 'clear.wav')
RUTA_GAMEOVER_SOUND = os.path.join(BASE_DIR, 'sounds', 'gameover.wav')


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

rotate_sound = None
line_clear_sound = None
game_over_sound = None

def cargar_sonidos():
    global rotate_sound, line_clear_sound, game_over_sound
    pygame.mixer.init()  # Inicializa el sistema de mezcla de sonidos
    rotate_sound = pygame.mixer.Sound(RUTA_ROTATE_SOUND)
    line_clear_sound = pygame.mixer.Sound(RUTA_CLEAR_SOUND)
    game_over_sound = pygame.mixer.Sound(RUTA_GAMEOVER_SOUND)
    


def iniciar_juego():
    cargar_sonidos()
    posiciones_bloqueadas = {}
    grilla = crear_grilla(posiciones_bloqueadas)
    cambio_de_pieza = False
    run = True
    pausado = False
    pieza_actual = generar_nueva_pieza()
    pieza_siguiente = generar_nueva_pieza()
    reloj = pygame.time.Clock()
    tiempo_de_caida_de_pieza = 0
    puntaje = 0
    velocidad_de_caida_de_pieza = 0.5

    # Cargar el puntaje más alto al inicio
    puntaje_alto = cargar_puntaje_alto()

    while run:
        grilla = crear_grilla(posiciones_bloqueadas)
        tiempo_de_caida_de_pieza += reloj.get_rawtime()
        reloj.tick()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pausado = not pausado

                if not pausado:
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
                        else:
                            rotate_sound.play()    
                    if event.key == pygame.K_SPACE:
                        while espacio_valido_para_pieza(pieza_actual, grilla):
                            pieza_actual.y += 1
                        pieza_actual.y -= 1  # Coloca la pieza en la última posición válida

        if not pausado:
            velocidad_de_caida_de_pieza = calcular_velocidad_caida(puntaje)

            if tiempo_de_caida_de_pieza / 1000 >= velocidad_de_caida_de_pieza:
                tiempo_de_caida_de_pieza = 0
                pieza_actual.y += 1
                if not espacio_valido_para_pieza(pieza_actual, grilla) and pieza_actual.y > 0:
                    pieza_actual.y -= 1
                    cambio_de_pieza = True

            shape_pos = celdas_ocupadas_en_tablero(pieza_actual)

            for x, y in shape_pos:
                if y > -1:
                    grilla[y][x] = pieza_actual.color

            if cambio_de_pieza:
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    posiciones_bloqueadas[p] = pieza_actual.color
                pieza_actual = pieza_siguiente
                pieza_siguiente = generar_nueva_pieza()
                cambio_de_pieza = False
                puntaje += eliminar_linea_completa(grilla, posiciones_bloqueadas) * 10

                # Actualiza el puntaje más alto
                if puntaje > puntaje_alto:
                    puntaje_alto = puntaje
                    guardar_puntaje_alto(puntaje_alto)

        renderizar_ventana_de_juego(pantalla, grilla, puntaje, pieza_siguiente, puntaje_alto)

        if pausado:
            pantalla.fill((0, 0, 0))
            generar_texto_puntaje("Juego en Pausa", 40, (255, 255, 255), pantalla, ANCHO_PANTALLA // 2 - 100, ALTURA_PANTALLA // 2 - 20)

        pygame.display.update()

        if not pausado and chequear_game_over(posiciones_bloqueadas):
            mostrar_menu_game_over(puntaje, puntaje_alto)
            break


def mostrar_menu_inicial(superficie):
    while True:
        superficie.fill((0, 0, 0))
        generar_texto_puntaje("Vitris", 60, (255, 255, 255), superficie, ANCHO_PANTALLA // 2 - 80, 100)
        generar_texto_puntaje("Controles:", 40, (255, 255, 255), superficie, ANCHO_PANTALLA // 2 - 90, 200)
        generar_texto_puntaje("Flechas: Mover la pieza", 30, (255, 255, 255), superficie, ANCHO_PANTALLA // 2 - 150, 250)
        generar_texto_puntaje("Flecha Arriba: Rotar la pieza", 30, (255, 255, 255), superficie, ANCHO_PANTALLA // 2 - 150, 300)
        generar_texto_puntaje("Flecha Abajo: Acelerar la caída", 30, (255, 255, 255), superficie, ANCHO_PANTALLA // 2 - 150, 350)
        generar_texto_puntaje("Espacio: Caída directa", 30, (255, 255, 255), superficie, ANCHO_PANTALLA // 2 - 150, 400)
        generar_texto_puntaje("P: Pausar / Reanudar", 30, (255, 255, 255), superficie, ANCHO_PANTALLA // 2 - 150, 450)
        generar_texto_puntaje("Presiona cualquier tecla para comenzar", 30, (255, 255, 255), superficie, ANCHO_PANTALLA // 2 - 180, 550)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:  # Cualquier tecla para continuar
                return


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
            game_over_sound.play()
            return True
    return False

def generar_nueva_pieza():
    #return Piece(5, 0, [[[1, 1], [1, 1]]]) # /// SIEMPRE CUADRADO PARA DESARROLLO
    return Piece(5, 0, random.choice(PIEZAS))  #/// PIEZAS RANDOM

def generar_texto_puntaje(text, size, color, surface, x, y):
    font = pygame.font.Font(None, size)
    label = font.render(text, 1, color)
    surface.blit(label, (x, y))

def dibujar_grilla(superficie, grilla):
    for y in range(len(grilla)):
        for x in range(len(grilla[y])):
            if grilla[y][x] != (0, 0, 0):  # Solo dibuja si hay un bloque
                pygame.draw.rect(
                    superficie, 
                    grilla[y][x],  # Color sólido
                    (TOP_LEFT_X + x * TAMANO_BLOQUE, TOP_LEFT_Y + y * TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE)
                )

    # Dibujar líneas de la cuadrícula
    for y in range(len(grilla)):
        pygame.draw.line(superficie, (128, 128, 128), (TOP_LEFT_X, TOP_LEFT_Y + y * TAMANO_BLOQUE),
                         (TOP_LEFT_X + ANCHO_DE_JUEGO, TOP_LEFT_Y + y * TAMANO_BLOQUE))
        for x in range(len(grilla[y])):
            pygame.draw.line(superficie, (128, 128, 128), (TOP_LEFT_X + x * TAMANO_BLOQUE, TOP_LEFT_Y),
                             (TOP_LEFT_X + x * TAMANO_BLOQUE, TOP_LEFT_Y + ALTO_DE_JUEGO))


def eliminar_linea_completa(grilla, locked):
    lineas_a_eliminar = 0
    filas_completas = []  # Para guardar las filas completas

    # Detectamos todas las filas completas
    for y in range(len(grilla) - 1, -1, -1):
        if (0, 0, 0) not in grilla[y]:  # Si no hay bloques vacíos en la fila
            filas_completas.append(y)  # Agregamos la fila completa a la lista

    # Si hay filas completas
    if filas_completas:
        lineas_a_eliminar = len(filas_completas)

        line_clear_sound.play()
        # Eliminar todas las posiciones de las filas completas en `locked`
        for y in filas_completas:
            for x in range(len(grilla[y])):
                if (x, y) in locked:
                    del locked[(x, y)]  # Borrar las posiciones bloqueadas de la fila

        # Desplazamos las filas superiores hacia abajo
        for pos in list(locked.keys()):
            x, y_pos = pos
            # Si la fila está por encima de la última fila eliminada
            if y_pos < filas_completas[0]:
                nueva_posicion = (x, y_pos + lineas_a_eliminar)  # Mover hacia abajo
                locked[nueva_posicion] = locked.pop(pos)

        # Mover las filas en la grilla
        for i in range(filas_completas[0], 0, -1):
            grilla[i] = grilla[i - lineas_a_eliminar][:]  # Copiar las filas superiores hacia abajo

        # Limpiar las primeras `lineas_a_eliminar` filas en la grilla
        for i in range(lineas_a_eliminar):
            grilla[i] = [(0, 0, 0) for _ in range(10)]  # Limpiar las filas superiores

    return lineas_a_eliminar

def calcular_velocidad_caida(puntaje):
    # Esto ajusta la velocidad de caída: por cada 100 puntos, la velocidad disminuye.
    # Ajusta los valores según lo que consideres adecuado para la jugabilidad.
    velocidad = 0.5 - (puntaje // 70) * 0.05
    return max(0.1, velocidad)  # La velocidad no puede ser menor a 0.1


def renderizar_ventana_de_juego(superficie, grilla, puntaje=0, proxima_pieza=None, puntaje_alto=0):
    superficie.fill((0, 0, 0))
    superficie.blit(fondo, (TOP_LEFT_X, TOP_LEFT_Y))
    dibujar_grilla(superficie, grilla)
    generar_texto_puntaje(f'Puntos: {puntaje}', 30, (255, 255, 255), superficie, 5, 20)
    
    # Mostrar el puntaje más alto
    generar_texto_puntaje(f'Highscore: {puntaje_alto}', 30, (255, 255, 255), superficie, 5, 60)
    
    dibujar_proxima_pieza(superficie, proxima_pieza)

    

def dibujar_proxima_pieza(superficie, pieza):
    # Tamaño de la zona para la próxima pieza
    x_offset = 460
    y_offset = 40
    zona_ancho = 4 * TAMANO_BLOQUE
    zona_alto = 4 * TAMANO_BLOQUE

    # Dibujar el texto "Próxima Pieza"
    font = pygame.font.Font(None, 25)
    texto = font.render("Próxima Pieza", True, (255, 255, 255))
    superficie.blit(texto, (x_offset, y_offset - 30))  # Texto sobre el recuadro

    # Obtener la forma de la pieza
    shape_format = pieza.shape[pieza.rotation % len(pieza.shape)]

    # Calcular tamaño real de la pieza
    pieza_ancho = len(shape_format[0]) * TAMANO_BLOQUE
    pieza_alto = len(shape_format) * TAMANO_BLOQUE

    # Calcular posición centrada dentro de la zona
    x_centrado = x_offset + (zona_ancho - pieza_ancho) // 2
    y_centrado = y_offset + (zona_alto - pieza_alto) // 2

    # Dibujar la pieza centrada
    for y, row in enumerate(shape_format):
        for x, cell in enumerate(row):
            if cell == 1:
                pygame.draw.rect(
                    superficie, pieza.color,
                    (x_centrado + x * TAMANO_BLOQUE, y_centrado + y * TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE)
                )

    # Dibujar un borde para la sección de la próxima pieza
    pygame.draw.rect(superficie, (255, 255, 255), (x_offset, y_offset, zona_ancho, zona_alto), 2)

def cargar_puntaje_alto():
    try:
        with open("puntaje_alto.txt", "r") as archivo:
            return int(archivo.read())
    except (FileNotFoundError, ValueError):
        return 0  # Si no existe el archivo o está vacío, la puntuación más alta es 0

def guardar_puntaje_alto(puntaje_alto):
    with open("puntaje_alto.txt", "w") as archivo:
        archivo.write(str(puntaje_alto))


def reiniciar_juego():
    iniciar_juego()

def mostrar_menu_game_over(puntaje, puntaje_alto):
    # Rellenar la pantalla de negro
    pantalla.fill((0, 0, 0))
    # Mostrar el título de Game Over
    generar_texto_puntaje("Game Over", 50, (255, 255, 255), pantalla, ANCHO_PANTALLA // 2 - 100, ALTURA_PANTALLA // 2 - 80)

    # Mostrar las opciones de reiniciar y salir
    generar_texto_puntaje("Presiona R para reiniciar", 30, (255, 255, 255), pantalla, ANCHO_PANTALLA // 2 - 130, ALTURA_PANTALLA // 2)
    generar_texto_puntaje("Presiona Q para salir", 30, (255, 255, 255), pantalla, ANCHO_PANTALLA // 2 - 110, ALTURA_PANTALLA // 2 + 40)
    # Mostrar el puntaje final
    generar_texto_puntaje(f'Puntaje final: {puntaje}', 30, (255, 255, 255), pantalla, ANCHO_PANTALLA // 2 - 100, ALTURA_PANTALLA // 2 + 80)
    # Mostrar el puntaje más alto
    generar_texto_puntaje(f'Puntaje más alto: {puntaje_alto}', 30, (255, 255, 255), pantalla, ANCHO_PANTALLA // 2 - 120, ALTURA_PANTALLA // 2 + 120)
    # Actualizar la pantalla
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reiniciar juego
                    reiniciar_juego()
                    return  # Salir del bucle y reiniciar
                if event.key == pygame.K_q:  # Salir del juego
                    pygame.quit()
                    sys.exit()

pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTURA_PANTALLA))
pygame.display.set_caption('Vitris')


try:
    fondo = pygame.image.load(RUTA_IMAGEN)
    fondo = pygame.transform.scale(fondo, (ANCHO_DE_JUEGO, ALTO_DE_JUEGO))
except pygame.error as e:
    print(f"Error al cargar la imagen: {e}")
    fondo = None

try:
    rotate_sound = pygame.mixer.Sound(RUTA_ROTATE_SOUND)
    line_clear_sound = pygame.mixer.Sound(RUTA_CLEAR_SOUND)
    game_over_sound = pygame.mixer.Sound(RUTA_GAMEOVER_SOUND)
except pygame.error as e:
    print(f"Error al cargar sonidos: {e}")


mostrar_menu_inicial(pantalla)
iniciar_juego()



