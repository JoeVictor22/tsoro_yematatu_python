# create an INET, STREAMing socket
import json
import socket
import threading


import rsa
from rsa import PublicKey, PrivateKey

from client.const import MAX_CHAR_MSG

SERVER_RSA_KEY = None

(PUBLIC_KEY, PRIVATE_KEY) = rsa.newkeys(2048)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c = None

DEFAULT_ENCODING = "utf-8"

ESTADO_JOGO = [None for _ in range(7)]
JOGADOR = None
COR_ADVERSARIO, COR_JOGADOR = None, None
SOCKET_THREAD = None
QUEM_DEVE_JOGAR = None
EU_DESISTO, ADVERSARIO_DESISTE = False, False
MESSAGE_BUFFER = [""]


def get_message(message):
    message = decrypt_message(message)
    message = message.decode()
    return json.loads(message)


def handle_connections(conexao, addr):
    global COR_ADVERSARIO, ESTADO_JOGO, SOCKET_THREAD, QUEM_DEVE_JOGAR

    while not SOCKET_THREAD.quit:
        message = conexao.recv(2048)
        if message != "":
            try:
                message = get_message(message)
                if message.get("event"):
                    print(f"[socket] {JOGADOR} : recebido : {message}")
                    if message["event"] == "COLOR":
                        COR_ADVERSARIO = message["color"]
                    if message["event"] == "FIRST":
                        QUEM_DEVE_JOGAR = message["color"]
                    elif message["event"] == "JOGADA_1":
                        realiza_jogada_1(message["index"], message["color"])
                    elif message["event"] == "JOGADA_2":
                        realiza_jogada_2(
                            message["index_1"], message["index_2"], message["color"]
                        )
                    elif message["event"] == "SURRENDER":
                        quer_desistir(message["color"])
                    elif message["event"] == "CHAT":
                        add_to_messages(message["message"], who=2)
            except Exception as e:
                print(e)
                pass


def realiza_jogada_1(posicao, cor):

    quantidade_de_jogadas = len([a for a in ESTADO_JOGO if a is not None])
    if ESTADO_JOGO[posicao] is None and quantidade_de_jogadas < 6:
        ESTADO_JOGO[posicao] = cor
        altera_jogador(cor)
        return True
    return False


def realiza_jogada_2(posicao_1, posicao_2, cor):
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
                altera_jogador(cor)
                return True
        return False


def altera_jogador(cor):
    global QUEM_DEVE_JOGAR
    QUEM_DEVE_JOGAR = COR_JOGADOR if cor == COR_ADVERSARIO else COR_ADVERSARIO


def send_event(data: "bytes"):
    socket = c or s
    socket.send(data)


def receive_encrypted(encrypted: str):
    json_as_string = decrypt_message(encrypted)
    message = json.loads(json_as_string)
    return message


def add_to_messages(message, who=0):
    global MESSAGE_BUFFER

    if message == "":
        return

    cat = "[info]: "
    if who == 1:
        cat = "[you]: "
    elif who == 2:
        cat = "[enemy]: "

    message = cat + message
    if len(MESSAGE_BUFFER) > 3:  # max msgs displayed
        MESSAGE_BUFFER.pop()
    MESSAGE_BUFFER.insert(0, message)


def primeiro_a_jogar(cor):
    global QUEM_DEVE_JOGAR

    if QUEM_DEVE_JOGAR is None:
        QUEM_DEVE_JOGAR = cor
        return True
    return False


def seleciona_cor(cor):
    global COR_JOGADOR, COR_ADVERSARIO

    if COR_ADVERSARIO and list(COR_ADVERSARIO) == list(cor):
        return False

    COR_JOGADOR = cor
    return True


def quer_desistir(cor):
    global EU_DESISTO, ADVERSARIO_DESISTE
    if cor == COR_JOGADOR:
        EU_DESISTO = True
    elif cor == COR_ADVERSARIO:
        ADVERSARIO_DESISTE = True


def send_encrypted(message: dict):
    global COR_JOGADOR, COR_ADVERSARIO, ESTADO_JOGO, QUEM_DEVE_JOGAR
    deny = False

    if message["event"] == "COLOR":
        deny = not seleciona_cor(message["color"])
    elif message["event"] == "FIRST":
        deny = not primeiro_a_jogar(message["color"])
    elif message["event"] == "JOGADA_1":
        deny = not realiza_jogada_1(message["index"], message["color"])
    elif message["event"] == "JOGADA_2":
        deny = not realiza_jogada_2(
            message["index_1"], message["index_2"], message["color"]
        )
    elif message["event"] == "CHAT":
        message["message"] = message["message"][:MAX_CHAR_MSG]
        add_to_messages(message["message"], who=1)
    elif message["event"] == "SURRENDER":
        quer_desistir(message["color"])

    if deny:
        return False

    message = json.dumps(message)
    print(f"[socket] {JOGADOR} : enviado : {message}")
    message = encrypt_message(message)
    send_event(message)
    return True


def encrypt_message(message: str, rsa_key=PUBLIC_KEY) -> bytes:
    message = message.encode(DEFAULT_ENCODING)
    encryped_msg = rsa.encrypt(message, rsa_key)
    return encryped_msg


def decrypt_message(message) -> str:
    decrypted_msg = rsa.decrypt(message, PRIVATE_KEY)
    return decrypted_msg


def create_client():
    # conecta a um server
    global JOGADOR
    JOGADOR = 2
    print("Tentando se conectar")
    s.connect(("127.0.0.1", 8123))
    global SOCKET_THREAD
    SOCKET_THREAD = threading.Thread(target=handle_connections, args=(s, "localhost"))
    SOCKET_THREAD.quit = False
    SOCKET_THREAD.start()
    print("Conectado")


def create_server():
    print("Criando primeira conexão.")
    global c, JOGADOR
    JOGADOR = 1
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(("127.0.0.1", 8123))
    s.listen(20)
    print("Aguardando jogador")
    c, addr = s.accept()
    global SOCKET_THREAD
    SOCKET_THREAD = threading.Thread(target=handle_connections, args=(c, addr))
    SOCKET_THREAD.quit = False
    SOCKET_THREAD.start()
