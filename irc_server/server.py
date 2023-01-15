import socket
import threading

class Channel:

    channels = {}

    def __init__(self) -> None:
        
        self.users = []

    def get_users(self):
        return self.users

class Server:

    def __init__(self) -> None:

        #channel name: channel instance
        self.channels = {}

        # nickname: connection
        self.users = {}
        
        self.instructions = {
            # "NICK": self.change_nickname,
            "QUIT": self.logout,
            "JOIN": self.join_channel,
            "LIST": self.list_channels
        }

    def login(self, conn) -> str:
        
        data = "Faça login com NICK <nickname>" 
        conn.send(data.encode())
        data = conn.recv(1024).decode().split(" ")
        while True:

            if data[0] != "NICK":
                data = "Faça login com NICK <nickname>" 
                conn.send(data.encode())
                data = conn.recv(1024).decode().split(" ")
                continue

            nickname = data[1]

            if nickname in self.users:
                data = "\nERR_NICKNAMEINUSE"
                conn.send(data.encode())
                continue
        
            break

        self.users[nickname] = conn
        print(nickname + " logged in")
        data = "Login successful"
        conn.send(data.encode())

        return nickname

    def logout(self, nickname, conn, param):
        conn.close()
        exit()
        
    def join_channel(self, nickname, conn, channel_name) -> None:
        
        if channel_name not in Channel.channels:
            current_channel = Channel()
            Channel.channels[channel_name] = current_channel
        current_channel =  Channel.channels[channel_name]
        
        current_channel.users.append(conn)

        data = "Connected to " + channel_name
        print(*Channel.channels[channel_name].users)
        conn.send(data.encode())

        data = ""
        while  True:
            data =  "<" + nickname + "> "+ conn.recv(1024).decode()
            for user_conn in current_channel.users:
                user_conn.send(data.encode())
        
        return

    def list_channels(self, nickname, conn, param):
        pass


    def thread_cliente(self, conn) -> None:

        nickname = self.login(conn)

        while True:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = conn.recv(1024).decode()
            print(nickname + " sent " + data)
            data = data.split(" ")

            instruction = data[0]
            if instruction in self.instructions:
                self.instructions[data[0]](nickname, conn, data[1])
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