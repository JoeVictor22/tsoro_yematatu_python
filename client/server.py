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
                pprint(packet)
                # this is a message sent
                """
                [thread] server: sent: {"event": "2client", "data": {"name": "sou o client"}}
                '{"event": "2server", "data": {"name": "sou o server"}}'
    
                """


def publish_event(event, data):
    socket = c or s
    packet = json.dumps({"event": event, "data": data})
    socket.send((packet + "\n").encode())
    print("[thread] server: sent: " + packet)


def send_event(event, data, publish=True, emit=True, bypass_turn=False):
    import time

    # time.sleep(2)
    publish_event(event, data)
    publish_event("2" + event, data)


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
    send_event("server", {"name": "sou o server"})

    return 1
