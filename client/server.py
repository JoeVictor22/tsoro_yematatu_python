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
CLIENT_ID = None
JOGADOR = None
COR_ADVERSARIO, COR_JOGADOR = None, None
def handle_server(conn, addr):
    global COR_ADVERSARIO, ESTADO_JOGO
    print("\nSERVER: ESPERANDO MSGS\n")
    while True:
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
                    elif message["event"] == "JOGADA_1":
                        realiza_jogada_1(message["index"], message["color"])
                    elif message["event"] == "JOGADA_2":
                        realiza_jogada_2(message["index_1"], message["index_2"], message["color"])
                    elif message["event"] == "CHAT":
                        add_to_messages(message["message"], who=2)

            except Exception as e:
                pprint(e)


def realiza_jogada_1(posicao, cor):
    quantidade_de_jogadas = len([a for a in ESTADO_JOGO if a is not None])
    print(quantidade_de_jogadas)
    if ESTADO_JOGO[posicao] is None and quantidade_de_jogadas < 6:
        ESTADO_JOGO[posicao] = cor
        return True
    return False

def realiza_jogada_2(posicao_1, posicao_2, cor):
    if ESTADO_JOGO[posicao_1] is None:
        # ESTADO_JOGO[posicao] = cor
        pprint("JOGADA 2")
        return True
    return False


def handle_client(conn, addr):
    global COR_ADVERSARIO, ESTADO_JOGO
    print("\nCLIENT: GAME LOOP\n")

    while True:
        """Game loop"""
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
                    elif message["event"] == "JOGADA_1":
                        realiza_jogada_1(message["index"], message["color"])
                    elif message["event"] == "JOGADA_2":
                        realiza_jogada_2(message["index_1"], message["index_2"], message["color"])
                elif message["event"] == "CHAT":
                        add_to_messages(message["message"], who=2)
            except Exception as e:
                pprint(e)


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




def send_encrypted(message: dict):
    global COR_JOGADOR, COR_ADVERSARIO, ESTADO_JOGO
    ## TODO: check event and alter server_state, deny if needed
    deny = False

    if message["event"] == "COLOR":
        pprint(COR_JOGADOR)
        pprint(COR_ADVERSARIO)
        pprint(message["color"])
        if COR_ADVERSARIO and list(COR_ADVERSARIO) == list(message["color"]):
            deny = True
        else:
            COR_JOGADOR = message["color"]
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
    t = threading.Thread(target=handle_client, args=(s, "localhost"))
    t.start()
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
    t = threading.Thread(target=handle_server, args=(c, addr))
    t.start()
    return 1
