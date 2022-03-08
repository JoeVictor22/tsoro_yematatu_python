if __name__ == "__main__":
    from client.server import create_connection
    from client.client import start_game

    create_connection()
    start_game()
