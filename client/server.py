# create an INET, STREAMing socket
import json
import socket
import threading
import time
import uuid

import rsa
from rsa import PublicKey, PrivateKey

SERVER_RSA_KEY = None

(PUBLIC_KEY, PRIVATE_KEY) = rsa.newkeys(1024)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c = None

DEFAULT_ENCODING = "utf-8"
from pprint import pprint

ESTADO_JOGO = [None for _ in range(7)]
CLIENT_ID = None
JOGADOR = None
COR_ADVERSARIO, COR_JOGADOR = None, None
# TODO: check cliente_id
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
                    if message["event"] == "JOGADA":
                        # TODO CHECK IF IS VALID
                        ESTADO_JOGO[message["index"]] = message["color"]

            except Exception as e:
                pprint(e)


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
                    if message["event"] == "JOGADA":
                        # TODO CHECK IF IS VALID
                        ESTADO_JOGO[message["index"]] = message["color"]

            except Exception as e:
                pprint(e)


def send_event(data: "bytes", publish=True, emit=True, bypass_turn=False):
    socket = c or s
    socket.send(data)


def send_public_key():
    socket = c
    pub_cert: bytes = PUBLIC_KEY.save_pkcs1()
    print("\n----ENVIOU-KEY----")
    socket.send(pub_cert)


def receive_encrypted(encrypted: str):
    json_as_string = decrypt_message(encrypted)
    print(f"[thread] : {JOGADOR}: {json_as_string}")
    message = json.loads(json_as_string)
    return message


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
    elif message["event"] == "JOGADA":
        index_jogada = message["index"]
        cor_jogada = message["color"]
        ESTADO_JOGO[index_jogada] = cor_jogada

    if deny:
        return False

    message = json.dumps(message)
    print(f"[thread] {JOGADOR} : sent: {message}")
    message = encrypt_message(message)
    send_event(message)
    return True


def encrypt_message(message: str, rsa_key=PUBLIC_KEY) -> bytes:
    """
    Convert a string to bytes and encrypt with RSA
    :param message:
    :return:
    """
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
