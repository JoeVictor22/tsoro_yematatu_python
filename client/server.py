# create an INET, STREAMing socket
import json
import socket
import threading
import time
import uuid

import rsa
from rsa import PublicKey, PrivateKey

SERVER_RSA_KEY = None

# (PUBLIC_KEY, PRIVATE_KEY) = rsa.newkeys(1024)
PUBLIC_KEY = PublicKey.load_pkcs1(b'-----BEGIN RSA PUBLIC KEY-----\nMIGJAoGBAJEr5hclMWjVjPJWG5ZiFhSvkABRhSVVjvxCViq9SdDWiIAlEbgK29QQ\nZmmBrlIjcXMdCQ3mMGJ5qqmjq+aHB+C+wFgz/OlKhtNw95HB0Ncggxhf0Zb3W3ZX\nvtsySMs6YNY6pXSKPttKPYcz38688XpmqP1eAuuqZslrJRzbJuOfAgMBAAE=\n-----END RSA PUBLIC KEY-----\n')
PRIVATE_KEY = PrivateKey.load_pkcs1(b'-----BEGIN RSA PRIVATE KEY-----\nMIICYAIBAAKBgQCRK+YXJTFo1YzyVhuWYhYUr5AAUYUlVY78QlYqvUnQ1oiAJRG4\nCtvUEGZpga5SI3FzHQkN5jBieaqpo6vmhwfgvsBYM/zpSobTcPeRwdDXIIMYX9GW\n91t2V77bMkjLOmDWOqV0ij7bSj2HM9/OvPF6Zqj9XgLrqmbJayUc2ybjnwIDAQAB\nAoGAVuxLHCa3/AaKG3x1jkjy4bXxak9lguJE+EScJYErlrEuEFSh1GokEEk1mQz+\nHM5+GqgTCNCAviYNiv+mEJS0hAURhCjo1X4Bq/o6TLXNHHpcu6jvpVH8FsCKvagi\nbvHmsKI67eVHE2i/mCLHST9jEL5aNCw0RglCeGWh3yuDMekCRQCT6WVVPj4Eblch\n7v2K8PhEqx8v/p5camEtH/4UOMV2mpOsKy/ck7VubUmNmz8wIZpWe7uzKfNa07rf\n1CqlCmBQcx4/lQI9APtB4BeRME6whF3VWbCpQ4OKHeq5DzWh3xIVtWTL9Bc80FEi\nZJHyuFM8GdtF3HU3MfCc48tpzAZMcJPZYwJFAIZ5WH6CgyHGK4OXY32xjRXpOgaJ\nh/JfaQ/8mSRLZQNqj72k2fPBet71jzymG3Gn60ibX9AI4M3/11Nt8oNwBpa9wo9t\nAjwfogSPkwTs80ZG9gRrvHO2jN4FXjUvAGkwQrFqtk7N2icz/8t/oHpaaFetBpeh\n3kgYTfhT9MbuCBOoWZcCRC+wMgnoS5pLHCqF+duRZPqo2AMKyC5UfnUK4nQhAhrx\nuJJMPGv2OVQWJwrx+sxG1oqcoGlSqrChg7hNdyI2b+ai8cRQ\n-----END RSA PRIVATE KEY-----\n')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c = None

DEFAULT_ENCODING = 'utf-8'
from pprint import pprint

CLIENT_ID = None
JOGADOR = None
# TODO: check cliente_id
def handle_server(conn, addr):
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
                    pprint(message)
            except Exception as e:
                pprint(e)

def handle_client(conn, addr):
    global SERVER_RSA_KEY
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
                    pprint(message)
            except Exception as e:
                pprint(e)


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
    print(f"[thread] : {JOGADOR}: {json_as_string}")
    message = json.loads(json_as_string)
    return message

def send_encrypted(message: dict):
    message = json.dumps(message)
    print(f"[thread] {JOGADOR} : sent: {message}")
    message = encrypt_message(message)
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
