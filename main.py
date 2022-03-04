if __name__ == "__main__":

    # # TESTE CLIENTE/SERVER
    from client.server import create_client, create_server

    try:
        create_client()
        # TESTE CLIENT GAME
        from client.client import print_game

        print_game()
    except Exception:
        create_server()
