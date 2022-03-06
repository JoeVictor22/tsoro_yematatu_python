# create an INET, STREAMing socket
import json
import socket
import threading
import time

import rsa
from rsa import PublicKey


SERVER_RSA_KEY = None

(PUBLIC_KEY, PRIVATE_KEY) = rsa.newkeys(1024)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c = None

DEFAULT_ENCODING = 'utf-8'
from pprint import pprint

JOGADOR_1, JOGADOR_2 = None, None

def handle_server(conn, addr):
    print("\nSERVER: ESPERANDO JOGADORES\n")
    global JOGADOR_1, JOGADOR_2
    while not JOGADOR_1 and not JOGADOR_2:
        """ Aguardando registro dos dois jogadores """
        send_public_key()
        message = conn.recv(1024)
        print("VAIVAIVAIVAI")
        if message != "":
            try:
                message = decrypt_message(message)
                print("Mensagem descriptografada")
                pprint(message)

                message = message.decode()
                message = json.loads(message)

                if message.get("event"):
                    if message["event"] == "REGISTER" and message.get("ID"):
                        if not JOGADOR_1:
                            JOGADOR_1 = message["ID"]
                        elif not JOGADOR_2:
                            JOGADOR_2 = message["ID"]

            except Exception as e:
                pprint(e)
                message = message.decode()
                print("MENSAGEM NAO CRIPTOGRAFADA")
                pprint(message)
                message = json.loads(message)
                if message.get("event"):
                    if message["event"] == "PUBLIC_KEY":
                        send_public_key()

    print("\nSERVER: ESPERANDO MSGS\n")

    while True:
        message = conn.recv(1024)
        if message != "":
            print("Servidor aguardando msgs")
            pprint(message)



        # from pprint import pprint
        # for packet in packets:
        #     if packet != "":
        #         message = decrypt_message(message)
        #
        #         pprint(message)
        #         if packet.get("event"):
        #             send_encrypted({"event_received": packet["event"]})
        #             pprint(packet)
        #             if packet["event"] == "REGISTER":
        #                 print("register")
        #                 # game_state.set_new_player()
        #                 # send_back ID
        #             if packet["event"] == "COLOR":
        #                 print("color")
        #                 # game_state.set_color(packet.get("color"), packet.get("id"))
        #             if packet["event"] == "JOGADA":
        #                 print("jogada")
        #                 # game_state.faz_jogada(packet.get("jogada"), packet.get("id"))
        #             if packet["event"] == "SURRENDER":
        #                 print("surrender")
        #                 # game_state.render(packet.get("id"))
        #             if packet["event"] == "MESSAGE":
        #                 print("message")


def handle_client(conn, addr):
    global SERVER_RSA_KEY
    print("\nCLIENT: ESPERANDO KEY\n")
    while not SERVER_RSA_KEY:
        from pprint import pprint

        """ Waiting for pub key """
        send_event(json.dumps({"event": "PUBLIC_KEY"}).encode())
        time.sleep(1)
        message = conn.recv(1024)

        if message != "":
            try:
                SERVER_RSA_KEY = PublicKey.load_pkcs1(message)
            except Exception as e:
                pprint(e)

    print("\nCLIENT: GAME LOOP\n")

    while True:
        """Game loop"""
        message = conn.recv(1024)
        from pprint import pprint

        message = message.decode(DEFAULT_ENCODING)
        packets = message.split("\n")
        for packet in packets:
            if packet != "":
                pprint(message)


from pprint import pprint

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
    print("[thread] : received: " + json_as_string)
    message = json.loads(json_as_string)
    return message


def send_encrypted(message: dict):
    message = json.dumps(message)
    print("[thread] server : sent: " + message)
    message = encrypt_message(message)
    send_event(message)

def send_encrypted_client(message: dict, rsa_key):
    message = json.dumps(message)
    print("[thread] client : sent: " + message)
    message = encrypt_message(message,rsa_key)
    send_event(message)


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
    print("Trying to connect")
    s.connect(("127.0.0.1", 8123))
    t = threading.Thread(target=handle_client, args=(s, "localhost"))
    t.start()

    print("Connected")

    return 2


def create_server():
    print("Not able to connect. Becoming the server.")
    global c
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 8123))
    s.listen(20)
    print("Waiting for connection")
    c, addr = s.accept()
    t = threading.Thread(target=handle_server, args=(c, addr))
    t.start()
    send_encrypted({"name": "sou o server"})

    return 1
