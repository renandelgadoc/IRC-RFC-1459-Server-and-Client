import socket
import threading
import os

def listen(socket):
    while True:
        data = socket.recv(1024).decode()  # receive response
        if not data:
            continue
        print(data)


def client_program():
    host = socket.gethostname()  # as both code is running on same pc
    port = 6667  # socket server port number
    # port = 6666

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
    client_socket.connect((host, port))  # connect to the server

    message = ""

    listen_thread = threading.Thread(target=listen, args=(client_socket,), daemon=True)
    listen_thread.start()

    while True:
        message = input()  # again take input
        client_socket.send(message.encode())
        if message.strip(" ") == 'QUIT':
            break

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()