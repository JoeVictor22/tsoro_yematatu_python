

game_states = ["COLORS", "PLAYING", "SURRENDER", "END"]
state = game_states[0]


jogador_turno = None
cores_jogadores = [None, None]
turnos = 0

def realizar_jogada():
    pass

def checar_vitoria():
    pass

"""Classe usada pelo server"""
def game_state():

    # loop
    if state == game_states[0]:
        # checar se as cores foram selecionadas, e deixar o player escolher
    elif state == game_states[1] or state == game_states[2]:
        if state == game_states[2]:
            # checar surrender
        else:
            # checar se jogada é valida e realizar
    elif state == game_states[3]:
        # fim de jogo
    else:
        # invalido


