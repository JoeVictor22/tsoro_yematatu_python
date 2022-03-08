import json, socket, threading, rsa
from socket import SOL_SOCKET, SO_REUSEADDR

from client.const import (
    MAX_CHAR_MSG,
    DEFAULT_ENCODING,
    PUBLIC_KEY,
    PRIVATE_KEY,
    ENDERECO,
    PORTA,
)

# Socket/conexão
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CONEXAO = None
SOCKET_THREAD = None

# Controle do jogo
ESTADO_JOGO = [None for _ in range(7)]
JOGADOR = None
COR_ADVERSARIO, COR_JOGADOR = None, None
QUEM_DEVE_JOGAR = None
EU_DESISTO, ADVERSARIO_DESISTE = False, False
MESSAGE_BUFFER = [""]


def get_message(message):
    message = decrypt_message(message)
    message = message.decode(DEFAULT_ENCODING)
    return json.loads(message)


def get_connection_message(conexao, _):
    global COR_ADVERSARIO, ESTADO_JOGO, SOCKET_THREAD, QUEM_DEVE_JOGAR

    while not SOCKET_THREAD.quit:
        message = conexao.recv(2048)
        if message == "":
            continue

        try:
            message = get_message(message)
            if not message.get("event"):
                continue

            print(f"[socket] {JOGADOR} : recebido : {message}")

            evento = message["event"]
            if evento == "COLOR":
                COR_ADVERSARIO = message["color"]
            if evento == "FIRST":
                QUEM_DEVE_JOGAR = message["color"]
            elif evento == "JOGADA_1":
                do_play_1(message["index"], message["color"])
            elif evento == "JOGADA_2":
                do_play_2(message["index_1"], message["index_2"], message["color"])
            elif evento == "SURRENDER":
                surrender(message["color"])
            elif evento == "CHAT":
                add_to_message_buffer(message["message"], who=2)
        except Exception:
            pass

    SOCKET.close()


def do_play_1(posicao, cor):

    quantidade_de_jogadas = len([a for a in ESTADO_JOGO if a is not None])
    if ESTADO_JOGO[posicao] is None and quantidade_de_jogadas < 6:
        ESTADO_JOGO[posicao] = cor
        change_player_turn(cor)
        return True
    return False


def do_play_2(posicao_1, posicao_2, cor):
    global QUEM_DEVE_JOGAR
    if ESTADO_JOGO[posicao_2] is None:
        jogada_realizada = [posicao_1, posicao_2]
        jogada_realizada.sort()
        # saltos permitidos
        jumps = [[0, 4], [0, 5], [0, 6], [1, 3], [4, 6]]
        moves = [
            [0, 1],
            [0, 2],
            [0, 3],
            [1, 2],
            [1, 4],
            [2, 3],
            [2, 5],
            [3, 6],
            [4, 5],
            [5, 6],
        ]

        for jogada in jumps + moves:
            if jogada_realizada == jogada:
                ESTADO_JOGO[posicao_1] = None
                ESTADO_JOGO[posicao_2] = cor
                change_player_turn(cor)
                return True
        return False


def change_player_turn(cor):
    global QUEM_DEVE_JOGAR
    QUEM_DEVE_JOGAR = COR_JOGADOR if cor == COR_ADVERSARIO else COR_ADVERSARIO


def send_message_to_peer(data: "bytes"):
    socket = CONEXAO or SOCKET
    socket.send(data)


def receive_encrypted(encrypted: str):
    json_as_string = decrypt_message(encrypted)
    message = json.loads(json_as_string)
    return message


def add_to_message_buffer(message, who=0):
    global MESSAGE_BUFFER

    if message == "":
        return

    cat = "[info]: "
    if who == 1:
        cat = "[you]: "
    elif who == 2:
        cat = "[enemy]: "

    message = cat + message
    if len(MESSAGE_BUFFER) > 3:
        MESSAGE_BUFFER.pop()
    MESSAGE_BUFFER.insert(0, message)


def first_to_play(cor):
    global QUEM_DEVE_JOGAR

    if QUEM_DEVE_JOGAR is None:
        QUEM_DEVE_JOGAR = cor
        return True
    return False


def pick_color(cor):
    global COR_JOGADOR, COR_ADVERSARIO

    if COR_ADVERSARIO and list(COR_ADVERSARIO) == list(cor):
        return False

    COR_JOGADOR = cor
    return True


def surrender(cor):
    global EU_DESISTO, ADVERSARIO_DESISTE
    if cor == COR_JOGADOR:
        EU_DESISTO = True
    elif cor == COR_ADVERSARIO:
        ADVERSARIO_DESISTE = True


def send_crypted(message: dict):
    global COR_JOGADOR, COR_ADVERSARIO, ESTADO_JOGO, QUEM_DEVE_JOGAR
    deny = False

    if message["event"] == "COLOR":
        deny = not pick_color(message["color"])
    elif message["event"] == "FIRST":
        deny = not first_to_play(message["color"])
    elif message["event"] == "JOGADA_1":
        deny = not do_play_1(message["index"], message["color"])
    elif message["event"] == "JOGADA_2":
        deny = not do_play_2(message["index_1"], message["index_2"], message["color"])
    elif message["event"] == "CHAT":
        message["message"] = message["message"][:MAX_CHAR_MSG]
        add_to_message_buffer(message["message"], who=1)
    elif message["event"] == "SURRENDER":
        surrender(message["color"])

    if deny:
        return False

    message = json.dumps(message)
    print(f"[socket] {JOGADOR} : enviado : {message}")
    message = encrypt_message(message)
    send_message_to_peer(message)
    return True


def encrypt_message(message: str, rsa_key=PUBLIC_KEY) -> bytes:
    message = message.encode(DEFAULT_ENCODING)
    encryped_msg = rsa.encrypt(message, rsa_key)
    return encryped_msg


def decrypt_message(message) -> str:
    decrypted_msg = rsa.decrypt(message, PRIVATE_KEY)
    return decrypted_msg


def create_connection():
    global CONEXAO, SOCKET, JOGADOR, SOCKET_THREAD
    try:
        JOGADOR = 2
        SOCKET.connect((ENDERECO, PORTA))
        SOCKET_THREAD = threading.Thread(
            name="Cliente", target=get_connection_message, args=(SOCKET, ENDERECO)
        )

    except Exception:
        JOGADOR = 1
        SOCKET.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        SOCKET.bind((ENDERECO, PORTA))

        SOCKET.listen()
        CONEXAO, endereco_da_conexao = SOCKET.accept()
        SOCKET_THREAD = threading.Thread(
            name="Servidor",
            target=get_connection_message,
            args=(CONEXAO, endereco_da_conexao),
        )

    SOCKET_THREAD.quit = False
    SOCKET_THREAD.start()
