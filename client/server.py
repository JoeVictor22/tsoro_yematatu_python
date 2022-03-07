# create an INET, STREAMing socket
import json
import socket
import threading
import time
import uuid

import rsa
from rsa import PublicKey, PrivateKey

from client.const import MAX_CHAR_MSG

SERVER_RSA_KEY = None

(PUBLIC_KEY, PRIVATE_KEY) = rsa.newkeys(2048)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c = None

DEFAULT_ENCODING = "utf-8"
from pprint import pprint

ESTADO_JOGO = [None for _ in range(7)]
JOGADOR = None
COR_ADVERSARIO, COR_JOGADOR = None, None
SOCKET_THREAD = None
QUEM_DEVE_JOGAR = None

def handle_connections(conn, addr):
    global COR_ADVERSARIO, ESTADO_JOGO, SOCKET_THREAD, QUEM_DEVE_JOGAR
    print("\nSERVER: ESPERANDO MSGS\n")

    while not SOCKET_THREAD.quit:
        message = conn.recv(1024)
        if message != "":
            try:
                message = decrypt_message(message)
                message = message.decode()
                message = json.loads(message)
                if message.get("event"):
                    print(f"[thread] {JOGADOR} : received: {message}")

                    if message["event"] == "COLOR":
                        COR_ADVERSARIO = message["color"]
                    if message["event"] == "FIRST":
                        QUEM_DEVE_JOGAR = message["color"]
                    elif message["event"] == "JOGADA_1":
                        realiza_jogada_1(message["index"], message["color"])
                    elif message["event"] == "JOGADA_2":
                        realiza_jogada_2(message["index_1"], message["index_2"], message["color"])
                    elif message["event"] == "CHAT":
                        add_to_messages(message["message"], who=2)

            except Exception:
                pass


def realiza_jogada_1(posicao, cor):

    quantidade_de_jogadas = len([a for a in ESTADO_JOGO if a is not None])
    print(quantidade_de_jogadas)
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
        jumps = [[0,4],[0,5],[0,6],[1,3],[4,6]]
        moves = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 4], [2, 3], [2, 5], [3, 6], [4, 5], [5, 6]]

        for jogada in jumps+moves:
            if jogada_realizada == jogada:
                ESTADO_JOGO[posicao_1] = None
                ESTADO_JOGO[posicao_2] = cor
                altera_jogador(cor)
                return True
        return False


def altera_jogador(cor):
    global QUEM_DEVE_JOGAR
    QUEM_DEVE_JOGAR = (COR_JOGADOR if cor == COR_ADVERSARIO else COR_ADVERSARIO)



# def handle_client(conn, addr):
#     global COR_ADVERSARIO, ESTADO_JOGO, SOCKET_THREAD
#     print("\nCLIENT: GAME LOOP\n")
#
#     while not SOCKET_THREAD.quit:
#         """Game loop"""
#         message = conn.recv(1024)
#         if message != "":
#             try:
#                 message = decrypt_message(message)
#                 message = message.decode()
#                 message = json.loads(message)
#                 if message.get("event"):
#                     print(f"[thread] {JOGADOR} : received: {message}")
#                     if message["event"] == "COLOR":
#                         COR_ADVERSARIO = message["color"]
#                     if message["event"] == "FIRST":
#                         primeiro_a_jogar(message["color"])
#                     elif message["event"] == "JOGADA_1":
#                         realiza_jogada_1(message["index"], message["color"])
#                     elif message["event"] == "JOGADA_2":
#                         realiza_jogada_2(message["index_1"], message["index_2"], message["color"])
#                 elif message["event"] == "CHAT":
#                         add_to_messages(message["message"], who=2)
#             except Exception:
#                 pass


def send_event(data: "bytes", publish=True, emit=True, bypass_turn=False):
    socket = c or s
    socket.send(data)


def receive_encrypted(encrypted: str):
    json_as_string = decrypt_message(encrypted)
    print(f"[thread] : {JOGADOR}: {json_as_string}")
    message = json.loads(json_as_string)
    return message


MESSAGE_BUFFER = [""]

def add_to_messages(message, who=0):
    global MESSAGE_BUFFER

    if message == "":
        return

    cat = "[info]: "
    if who == 1:
        cat = "[you]: "
    elif who ==2:
        cat = "[enemy]: "

    message = cat + message
    if len(MESSAGE_BUFFER) > 3: # max msgs displayed
        MESSAGE_BUFFER.pop()
    MESSAGE_BUFFER.insert(0, message)



def primeiro_a_jogar(cor):
    global QUEM_DEVE_JOGAR
    print("primeiro")
    print(cor)
    print(QUEM_DEVE_JOGAR)
    if QUEM_DEVE_JOGAR is None:
        QUEM_DEVE_JOGAR = cor
        print("eh vc")
        return True
    print("n ehvc")
    return False

def seleciona_cor(cor):
    global COR_JOGADOR, COR_ADVERSARIO

    if COR_ADVERSARIO and list(COR_ADVERSARIO) == list(cor):
        return False

    COR_JOGADOR = cor
    return True

def send_encrypted(message: dict):
    global COR_JOGADOR, COR_ADVERSARIO, ESTADO_JOGO, QUEM_DEVE_JOGAR
    ## TODO: check event and alter server_state, deny if needed
    deny = False

    if message["event"] == "COLOR":
        deny = not seleciona_cor(message["color"])
    elif message["event"] == "FIRST":
        deny = not primeiro_a_jogar(message["color"])
    elif message["event"] == "JOGADA_1":
        deny = not realiza_jogada_1(message["index"], message["color"])
    elif message["event"] == "JOGADA_2":
        deny = not realiza_jogada_2(message["index_1"], message["index_2"], message["color"])
    elif message["event"] == "CHAT":
        message["message"] = message["message"][:MAX_CHAR_MSG]
        add_to_messages(message["message"], who=1)

    if deny:
        return False

    message = json.dumps(message)
    print(f"[thread] {JOGADOR} : sent: {message}")
    message = encrypt_message(message)
    send_event(message)
    return True


def encrypt_message(message: str, rsa_key=PUBLIC_KEY) -> bytes:
    message = message.encode(DEFAULT_ENCODING)
    encryped_msg = rsa.encrypt(message, rsa_key)
    return encryped_msg


def decrypt_message(message) -> str:
    decrypted_msg = rsa.decrypt(message, PRIVATE_KEY)
    # decrypted_msg = decrypted_msg.decode(DEFAULT_ENCODING)
    return decrypted_msg


def create_client():
    # conecta a um server
    global JOGADOR
    JOGADOR = 2
    print("Trying to connect")
    s.connect(("127.0.0.1", 8123))
    global SOCKET_THREAD
    SOCKET_THREAD = threading.Thread(target=handle_connections, args=(s, "localhost"))
    SOCKET_THREAD.quit = False
    SOCKET_THREAD.start()
    print("Connected")
    return 2


def create_server():
    print("Not able to connect. Becoming the server.")
    global c, JOGADOR
    JOGADOR = 1
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 8123))
    s.listen(20)
    print("Waiting for connection")
    c, addr = s.accept()
    global SOCKET_THREAD
    SOCKET_THREAD = threading.Thread(target=handle_connections, args=(c, addr))
    SOCKET_THREAD.quit = False
    SOCKET_THREAD.start()

    return 1

