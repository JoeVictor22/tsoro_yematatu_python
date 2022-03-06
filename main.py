if __name__ == "__main__":

    # # TESTE CLIENTE/SERVER
    from client.server import create_client, create_server
    from client.client import  game_opening

    try:
        create_client()
        game_opening()
    except Exception:
        create_server()
        game_opening(False)
