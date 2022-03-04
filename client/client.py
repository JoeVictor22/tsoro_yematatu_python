import pygame as pg
import time
from pygame.locals import *

# based on https://techvidvan.com/tutorials/python-game-project-tic-tac-toe/
# initialize global variables
XO = "x"
winner = None
draw = False
width = 400
height = 400
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0 , 0)
green = (0, 255, 0)
blue = (0, 0, 255)
line_color = black
# TicTacToe 3x3 board
GAME = [0 for _ in range(7)]
player_color = None
cores_matrix = [[red, green, blue], [red, green, blue], [red, green, blue]]

pg.init()
fps = 30
CLOCK = pg.time.Clock()
screen = pg.display.set_mode((width, height + 100), 0, 32)
pg.display.set_caption("Tsoro Yematatu")
size_circle_game = 15
size_circle_color = 50
expessura_linha = int(size_circle_game/2)


posicoes_selecoes = [
                        [width / 2, height / 6],
                        [0, 0],[width / 2, height / 2], [0, 0],
    [width / 6, height / 1.2], [width / 2, height / 1.2], [height / 1.2, height / 1.2]
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


def draw_text(message):

    font = pg.font.Font(None, 30)
    text = font.render(message, 1, (255, 255, 255))
    # copy the rendered message onto the board
    screen.fill((0, 0, 0), (0, width, width, height))
    text_rect = text.get_rect(center=(width / 2, height + height/10))
    screen.blit(text, text_rect)
    pg.display.update()

def game_opening():
    screen.blit(opening, (0, 0))
    pg.display.update()
    pg.draw.circle(screen, white, (width/2, height/2), width/3)
    time.sleep(1)
    screen.fill(white)

    global cores_matrix
    pg.draw.circle(screen, cores_matrix[0][0], (width / 6, height / 6), size_circle_color)
    pg.draw.circle(screen, cores_matrix[0][1], (width / 2, height / 6), size_circle_color)
    pg.draw.circle(screen, cores_matrix[0][2], (height/1.2 , height / 6), size_circle_color)
    pg.draw.circle(screen, cores_matrix[1][0], (width / 6, height / 2), size_circle_color)
    pg.draw.circle(screen, cores_matrix[1][1], (width / 2, height / 2), size_circle_color)
    pg.draw.circle(screen, cores_matrix[1][2], (height/1.2 , height / 2), size_circle_color)
    pg.draw.circle(screen, cores_matrix[2][0], (width / 6, height / 1.2), size_circle_color)
    pg.draw.circle(screen, cores_matrix[2][1], (width / 2, height / 1.2), size_circle_color)
    pg.draw.circle(screen, cores_matrix[2][2], (height/1.2 , height / 1.2), size_circle_color)

    draw_text("Selecione sua cor")

def draw_game():
    screen.fill(white)

    global cores_matrix

    linhas = []
    linhas.append([posicoes_selecoes[0], posicoes_selecoes[4]])
    linhas.append([posicoes_selecoes[0], posicoes_selecoes[5]])
    linhas.append([posicoes_selecoes[0], posicoes_selecoes[6]])
    linhas.append([posicoes_selecoes[1], posicoes_selecoes[3]])
    linhas.append([posicoes_selecoes[4], posicoes_selecoes[6]])

    for linha in linhas:
      pg.draw.line(screen, line_color, linha[0], linha[1], expessura_linha)


    pg.draw.circle(screen, cores_matrix[0][1],posicoes_selecoes[0], size_circle_game)
    pg.draw.circle(screen, cores_matrix[1][0],posicoes_selecoes[1], size_circle_game)
    pg.draw.circle(screen, cores_matrix[1][1],posicoes_selecoes[2], size_circle_game)
    pg.draw.circle(screen, cores_matrix[1][2],posicoes_selecoes[3], size_circle_game)
    pg.draw.circle(screen, cores_matrix[2][0],posicoes_selecoes[4], size_circle_game)
    pg.draw.circle(screen, cores_matrix[2][1],posicoes_selecoes[5], size_circle_game)
    pg.draw.circle(screen, cores_matrix[2][2],posicoes_selecoes[6], size_circle_game)


    draw_text("faz a jogada ai")

def check_win():
    # check for winning rows
    pg.draw.line(screen, (250, 70, 70), (350, 50), (50, 350), 4)
    draw_text("venceu???")


def reset_game():
    game_opening()


def get_color():
    from client.server import send_event
    global player_color
    # get coordinates of mouse click
    x, y = pg.mouse.get_pos()
    row, col = get_box_selected(x, y)
    print(row, col)
    global cores_matrix
    print(cores_matrix)
    if row is not None and col is not None:
        send_event("selecionei a cor", {"x": x, "y": y})
        player_color = cores_matrix[row][col]
        print("escolhi a cor")

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

def get_circle_selected(x,y):
    row, col = None, None

    for i, posicao in enumerate(posicoes_selecoes):
        ponto_x, ponto_y = posicao[0],posicao[1]
        ponto_tam = size_circle_game
        if (x >= ponto_x - (ponto_tam) and x <= ponto_x + (ponto_tam) and y >= ponto_y - (ponto_tam) and y <= ponto_y + (ponto_tam)):
            print(f"ponto {i}: {posicoes_selecoes[i][0]}, {posicoes_selecoes[i][1]}")



    return row, col

def get_click():
    # get coordinates of mouse click
    x, y = pg.mouse.get_pos()
    print(x,y)
    return x,y

def get_jogada():
    row,col =get_circle_selected(*get_click())
    print("escolheu", row, col)

import sys

game_opening()

while player_color is None:
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            # the user clicked; place an X or O
            get_color()
    pg.display.update()
    CLOCK.tick(fps)
print("ACABOU")


# run the game loop forever
while True:
    draw_game()

    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            # the user clicked; place an X or O
            get_jogada()
            # if False:
            #     reset_game()
    pg.display.update()
    CLOCK.tick(fps)


