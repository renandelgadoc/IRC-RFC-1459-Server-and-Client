import socket
import threading

class Channel:

    channels = {}

    def __init__(self) -> None:
        
        self.users = []

class Server:

    def __init__(self) -> None:

        #channel name: channel instance
        self.channels = {}

        # username: connection
        self.users = {}
        
        self.instructions = {
            # "NICK": self.change_username,
            "QUIT": self.logout,
            "JOIN": self.join_channel,
            "LIST": self.list_channels
        }

    def login(self, conn) -> str:

        data = "Faça login com USER <username>"
        conn.send(data.encode())

        data = conn.recv(1024).decode().split(" ")

        while True:

            if data[0] != "USER":
                data = "Login before using a chat"
                conn.send(data.encode())
                data = conn.recv(1024).decode().split(" ")
                continue

            username = data[1]

            if username in self.users:
                data = "Usuário já logado"
                conn.send(data.encode())
                continue
        
            break

        self.users[username] = conn
        print(username + " logged in")
        data = "Login successful"
        conn.send(data.encode())

        return username

    def logout(self, username, conn, param):
        conn.close()
        exit()
        
    def join_channel(self, username, conn, channel_name) -> None:
        
        if channel_name not in Channel.channels:
            current_channel = Channel()
            Channel.channels[channel_name] = current_channel
        current_channel =  Channel.channels[channel_name]
        
        current_channel.users.append(conn)

        data = "Connected to " + channel_name
        print(*Channel.channels[channel_name].users)
        conn.send(data.encode())

        data = ""
        while  data.split(" ")[0] != "PART":
            data = conn.recv(1024).decode()
            for user_conn in current_channel.users:
                user_conn.send(data.encode())
        
        return

    def list_channels(self, username, conn, param):
        pass


    def thread_cliente(self, conn) -> None:

        username = self.login(conn)

        while True:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = conn.recv(1024).decode()
            print(username + " sent " + data)
            data = data.split(" ")

            instruction = data[0]
            if instruction in self.instructions:
                self.instructions[data[0]](username, conn, data[1])
            else:
                data = "Instruction not valid"
                conn.send(data.encode())
                continue


    def server_program(self) -> None:
        # get the hostname
        host = socket.gethostname()
        port = 6667  # initiate port no above 1024

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
        # look closely. The bind() function takes tuple as argument
        server_socket.bind((host, port))  # bind host address and port together

        # configure how many client the server can listen simultaneously
        server_socket.listen(2)
        
        while True:
            conn, address = server_socket.accept()  # accept new connection
            print("Connection from: " + str(address))
            x = threading.Thread(target=self.thread_cliente, args=(conn,), daemon=True)
            x.start()


if __name__ == '__main__':
    server = Server()
    server.server_program()