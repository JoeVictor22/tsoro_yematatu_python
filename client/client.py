from copy import deepcopy

import pygame as pg
import time
from pygame.locals import *

# based on https://techvidvan.com/tutorials/python-game-project-tic-tac-toe/
# initialize global variables
from client.server import send_encrypted, add_to_messages

XO = "x"
winner = None
draw = False
from client.const import *

line_color = black
# TicTacToe 3x3 board
GAME = [0 for _ in range(7)]
player_color = None
cores_matrix = [[red, green, blue], [yellow, cyan, magenta], [orange, brown, pink]]

import uuid

MY_UUID = str(uuid.uuid4())
pg.init()
fps = 30
CLOCK = pg.time.Clock()
screen = pg.display.set_mode((width, height + 100), 0, 32)
pg.display.set_caption("Tsoro Yematatu")
size_circle_game = 15
size_circle_color = 50
expessura_linha = int(size_circle_game / 2)

#
EMPATE = [False, False]
COR_JOGADOR, COR_ADVERSARIO = None, None
EH_MINHA_JOGADA = False
ESTADO_JOGO = [None for _ in range(7)]


posicoes_selecoes = [
    [width / 2, height / 6],
    [0, 0],
    [width / 2, height / 2],
    [0, 0],
    [width / 6, height / 1.2],
    [width / 2, height / 1.2],
    [height / 1.2, height / 1.2],
]

# Calculo de ponto medio
posicoes_selecoes[1][0] = (posicoes_selecoes[0][0] + posicoes_selecoes[4][0]) / 2
posicoes_selecoes[1][1] = (posicoes_selecoes[0][1] + posicoes_selecoes[4][1]) / 2
posicoes_selecoes[3][0] = (posicoes_selecoes[0][0] + posicoes_selecoes[6][0]) / 2
posicoes_selecoes[3][1] = (posicoes_selecoes[0][1] + posicoes_selecoes[6][1]) / 2


# loading the images
opening = pg.image.load("background.png")
# resizing images
opening = pg.transform.scale(opening, (width, height + 100))


INPUT_MESSAGE_BUFFER = ""
INPUT_BUFFER = ""
def get_input(event):
    charset = "abcdefghijklmnopqrstuvyxwz1234567890?!.,"
    if event.key == pg.K_RETURN:
        enviar_input_buffer()
    elif event.key == pg.K_SPACE:
        add_to_input_buffer(" ")
    elif event.key == pg.K_BACKSPACE:
        backspace_to_input_buffer()
    elif pg.key.name(event.key) in charset:
        add_to_input_buffer(pg.key.name(event.key))


def enviar_input_buffer():
    global INPUT_BUFFER
    send_message(INPUT_BUFFER)
    clear_input_buffer()

def clear_input_buffer():
    global INPUT_BUFFER
    INPUT_BUFFER = ""

def add_to_input_buffer(key:str):
    global INPUT_BUFFER
    if len(INPUT_BUFFER) > MAX_CHAR_MSG:
        INPUT_BUFFER = INPUT_BUFFER[1:]
    INPUT_BUFFER += key

def backspace_to_input_buffer():
    global INPUT_BUFFER
    INPUT_BUFFER = INPUT_BUFFER[:-1]

def draw_chat():
    global INPUT_BUFFER
    from client.server import MESSAGE_BUFFER
    buffer = MESSAGE_BUFFER.copy()
    buffer.insert(0, INPUT_BUFFER)
    font_size = 20
    font = pg.font.Font(None, font_size)

    screen.fill((0, 0, 0), (0, width, width, height)) # box


    added_height = int(font_size/100*70)
    padding = int(font_size/100*20)
    for idx, message in enumerate(buffer):
        iter_message = message
        text_color = green

        if idx == 0:
            text_color = white
            if message == "":
                iter_message = "Digite algo e envie pressionando ENTER!"


        if message.startswith("[info]"):
            text_color = cyan

        if message.startswith("[enemy]"):
            text_color = red



        text = font.render(str(iter_message), True, text_color)
        text.get_rect()
        text_rect = text.get_rect(left=padding, top= (height + height/4 - added_height))
        added_height += font_size
        screen.blit(text, text_rect)

    pg.display.update()


def game_opening(register=True):

    if register:
        send_register()
    screen.blit(opening, (0, 0))
    pg.display.update()
    time.sleep(1)
    screen.fill(white)

    global cores_matrix, COR_ADVERSARIO
    pg.draw.circle(
        screen, cores_matrix[0][0], (width / 6, height / 6), size_circle_color
    )
    pg.draw.circle(
        screen, cores_matrix[0][1], (width / 2, height / 6), size_circle_color
    )
    pg.draw.circle(
        screen, cores_matrix[0][2], (height / 1.2, height / 6), size_circle_color
    )
    pg.draw.circle(
        screen, cores_matrix[1][0], (width / 6, height / 2), size_circle_color
    )
    pg.draw.circle(
        screen, cores_matrix[1][1], (width / 2, height / 2), size_circle_color
    )
    pg.draw.circle(
        screen, cores_matrix[1][2], (height / 1.2, height / 2), size_circle_color
    )
    pg.draw.circle(
        screen, cores_matrix[2][0], (width / 6, height / 1.2), size_circle_color
    )
    pg.draw.circle(
        screen, cores_matrix[2][1], (width / 2, height / 1.2), size_circle_color
    )
    pg.draw.circle(
        screen, cores_matrix[2][2], (height / 1.2, height / 1.2), size_circle_color
    )

    add_to_messages("Selecione sua cor")

    import sys

    while COR_JOGADOR is None or COR_ADVERSARIO is None:
        draw_chat()
        from client.server import COR_ADVERSARIO


        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and COR_JOGADOR is None:
                # the user clicked; place an X or O
                get_color()
            elif event.type == pg.KEYDOWN:
                get_input(event)

        pg.display.update()
        CLOCK.tick(fps)

    add_to_messages("Jogo iniciado")

    # run the game loop forever
    while True:
        draw_game()
        if check_win():
            time.sleep(1)
            add_to_messages("Fim de jogo")
            time.sleep(2)
            break

        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                # the user clicked; place an X or O
                get_jogada()

                # if False:
                #     reset_game()
            elif event.type == pg.KEYDOWN:
                get_input(event)
        pg.display.update()
        CLOCK.tick(fps)

    sys.exit(0)

def draw_game():
    screen.fill(white)
    global cores_matrix, ESTADO_JOGO
    from client.server import ESTADO_JOGO

    linhas = []
    linhas.append([posicoes_selecoes[0], posicoes_selecoes[4]])
    linhas.append([posicoes_selecoes[0], posicoes_selecoes[5]])
    linhas.append([posicoes_selecoes[0], posicoes_selecoes[6]])
    linhas.append([posicoes_selecoes[1], posicoes_selecoes[3]])
    linhas.append([posicoes_selecoes[4], posicoes_selecoes[6]])

    for linha in linhas:
        pg.draw.line(screen, line_color, linha[0], linha[1], expessura_linha)

    for idx, _ in enumerate(ESTADO_JOGO):
        cor = ESTADO_JOGO[idx]
        posicao = posicoes_selecoes[idx]

        if IDX_SELECIONADO == idx:
            pg.draw.circle(
                screen, black, posicao, int(size_circle_game * 1.3)
            )

        pg.draw.circle(
            screen, cor or black, posicao, size_circle_game
        )


    draw_chat()



def check_win():
    # check for winning rows

    vitorias = [
        [0, 1, 4],
        [0, 2, 5],
        [0, 3, 6],
        [1, 2, 3],
        [4, 5, 6]
    ]

    from client.server import ESTADO_JOGO
    vencedor = None
    for vitoria in vitorias:
        if ESTADO_JOGO[vitoria[0]] is None:
            continue

        if ESTADO_JOGO[vitoria[0]] == ESTADO_JOGO[vitoria[1]] and ESTADO_JOGO[vitoria[1]] == ESTADO_JOGO[vitoria[2]]:
            vencedor = ESTADO_JOGO[vitoria[0]]
            break
    if vencedor == COR_JOGADOR:
        add_to_messages("Você venceu")
    elif vencedor:
        add_to_messages("Você perdeu")


def reset_game():
    game_opening()


def get_color():
    global COR_JOGADOR
    # get coordinates of mouse click
    x, y = pg.mouse.get_pos()
    row, col = get_box_selected(x, y)
    global cores_matrix
    if row is not None and col is not None:
        COR_JOGADOR = cores_matrix[row][col]

        if not send_color():
            add_to_messages("Cor já selecionada...")
            COR_JOGADOR = None
        else:
            add_to_messages("Aguardando outro jogador...")


def send_message_to_server(message: dict):
    message["id"] = MY_UUID
    return send_encrypted(message)


def send_surrender():
    return send_message_to_server({"event": "SURRENDER"})


def send_register():
    return send_message_to_server({"event": "REGISTER"})


def send_color():
    return send_message_to_server({"event": "COLOR", "color": COR_JOGADOR})


def send_jogada_1(index_jogada):
    add_to_messages(f"Jogada: {index_jogada}")
    return send_message_to_server(
        {"event": "JOGADA_1", "index": index_jogada, "color": COR_JOGADOR}
    )

def send_jogada_2(index_jogada_1, index_jogada_2):
    add_to_messages(f"Jogada: {index_jogada_1} -> {index_jogada_2}")
    return send_message_to_server(
        {"event": "JOGADA_2", "index_1": index_jogada_1, "index_2": index_jogada_2, "color": COR_JOGADOR}
    )


def send_message(message):
    return send_message_to_server({"event": "CHAT", "message": message})


def get_box_selected(x, y):
    row, col = None, None
    # get column of mouse click (1-3)
    if x < width / 3:
        col = 0
    elif x < width / 3 * 2:
        col = 1
    elif x < width:
        col = 2
    else:
        col = None

    # get row of mouse click (1-3)
    if y < height / 3:
        row = 0
    elif y < height / 3 * 2:
        row = 1
    elif y < height:
        row = 2
    else:
        row = None

    return row, col


def get_circle_selected(x, y):
    row, col, i = None, None, None

    for i, posicao in enumerate(posicoes_selecoes):
        ponto_x, ponto_y = posicao[0], posicao[1]
        ponto_tam = size_circle_game
        if (
            x >= ponto_x - (ponto_tam)
            and x <= ponto_x + (ponto_tam)
            and y >= ponto_y - (ponto_tam)
            and y <= ponto_y + (ponto_tam)
        ):
            row, col = posicoes_selecoes[i][0], posicoes_selecoes[i][1]
            break
    return row, col, i


def get_click():
    # get coordinates of mouse click
    x, y = pg.mouse.get_pos()
    return x, y

IDX_SELECIONADO = None
def jogada_multipla(index_jogada):
    global IDX_SELECIONADO
    from client.server import ESTADO_JOGO

    if IDX_SELECIONADO == index_jogada:
        IDX_SELECIONADO = None
    elif IDX_SELECIONADO is None and ESTADO_JOGO[index_jogada] == COR_JOGADOR:
        IDX_SELECIONADO = index_jogada
    elif IDX_SELECIONADO is not None and ESTADO_JOGO[index_jogada] is None:
        idx_1 = deepcopy(IDX_SELECIONADO)
        send_jogada_2(idx_1, index_jogada)
        IDX_SELECIONADO = None

def get_jogada():
    row, col, index_jogada = get_circle_selected(*get_click())
    from client.server import ESTADO_JOGO
    if row:
        quantidade_de_jogadas = len([a for a in ESTADO_JOGO if a is not None])
        if quantidade_de_jogadas < 6:
            send_jogada_1(index_jogada)
        else:
            jogada_multipla(index_jogada)