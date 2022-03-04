# create an INET, STREAMing socket
import json
import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c = None


def handle_client(conn, addr):
    while True:
        message = conn.recv(1024)
        message = message.decode()
        packets = message.split("\n")
        from pprint import pprint

        for packet in packets:

            if packet != "":
                packet = json.loads(packet)
                pprint(packet)

                if packet.get("event"):
                    send_event({"event_received": packet["event"]})
                    pprint(packet)
                    if packet["event"] == "REGISTER":
                        print("register")
                        # game_state.set_new_player()
                        # send_back ID
                    if packet["event"] == "COLOR":
                        print("color")
                        # game_state.set_color(packet.get("color"), packet.get("id"))
                    if packet["event"] == "JOGADA":
                        print("jogada")
                        # game_state.faz_jogada(packet.get("jogada"), packet.get("id"))
                    if packet["event"] == "SURRENDER":
                        print("surrender")
                        # game_state.render(packet.get("id"))
                    if packet["event"] == "MESSAGE":
                        print("message")

def publish_event(data):
    socket = c or s
    packet = json.dumps(data)
    socket.send((packet + "\n").encode())
    print("[thread] server: sent: " + packet)


def send_event( data, publish=True, emit=True, bypass_turn=False):
    publish_event(data)


def create_client():
    # conecta a um server
    print("Trying to connect")
    s.connect(("127.0.0.1", 8123))
    t = threading.Thread(target=handle_client, args=(s, "localhost"))
    t.start()

    print("Connected")

    return 2


def create_server():
    # cria um server
    print("Not able to connect. Becoming the server.")
    global c
    # No one listening, become the server
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 8123))
    s.listen(20)
    print("Waiting for connection")
    c, addr = s.accept()
    t = threading.Thread(target=handle_client, args=(c, addr))
    t.start()
    send_event({"name": "sou o server"})

    return 1
