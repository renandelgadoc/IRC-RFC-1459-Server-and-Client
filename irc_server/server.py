import socket
import threading

class Channel:

    channels = {}

    def __init__(self) -> None:
        
        self.users = {}

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

        while True:

            data = "Faça login com NICK <nickname>" 
            conn.send(data.encode())
            data = conn.recv(1024).decode().split(" ")

            if len(data) == 1:
                data = "Nickname name not specified\n"
                conn.send(data.encode())
                continue
            elif len(data) > 2:
                data = "Invalid character in nickname\n"
                conn.send(data.encode())
                continue
            elif data[0] != "NICK":
                continue

            nickname = data[1]

            if nickname in self.users:
                data = "ERR_NICKNAMEINUSE"
                conn.send(data.encode())
                continue
        
            break

        self.users[nickname] = conn
        print(nickname + " logged in")
        data = "Login successful"
        conn.send(data.encode())

        return nickname

    def logout(self, nickname, conn, params):
        conn.close()
        exit()
        
    def join_channel(self, nickname, conn, params) -> None:

        if len(params) == 1:
            data = "Channel name not specified"
            conn.send(data.encode())
            return
        elif len(params) > 2:
            data = "It is only possible to join one channel at a time"
            conn.send(data.encode())
            return
        channel_name = params[1]

        if channel_name not in Channel.channels:
            current_channel = Channel()
            Channel.channels[channel_name] = current_channel
        current_channel =  Channel.channels[channel_name]
        
        current_channel.users[nickname] = conn

        data = "Connected to " + channel_name
        print(*Channel.channels[channel_name].users)
        conn.send(data.encode())

        data = ""
        while  True:
            data =conn.recv(1024).decode()
            if "PART" in data:
                data = nickname + " left the server"
                for user in current_channel.users:
                    current_channel.users[user].send(data.encode())
                del current_channel.users[nickname]
                break
            data =   "<" + nickname + "> " + data
            for user in current_channel.users:
                current_channel.users[user].send(data.encode())
        
        return

    def list_channels(self, nickname, conn, params):
        pass


    def thread_cliente(self, conn) -> None:

            nickname = self.login(conn)

            while True:
                try:

                    # receive data stream. it won't accept data packet greater than 1024 bytes
                    data = conn.recv(1024).decode()
                    print(nickname + " sent " + data)

                    # Remove space duplicates and split input in a list
                    data = " ".join(data.split(" "))
                    data = data.split(" ")

                    # Check if the instruction is valid and call corresponding function
                    instruction = data[0]
                    if instruction in self.instructions:
                        self.instructions[data[0]](nickname, conn, data)
                    else:
                        data = "Instruction not valid"
                        conn.send(data.encode())
                        continue

                except:
                    print("Error")
                    data = "Server Error"
                    conn.send(data.encode())


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

            # Start a new thread for a client and close connection if anything goes wrong
            x = threading.Thread(target=self.thread_cliente, args=(conn,), daemon=True)
            x.start()

if __name__ == '__main__':
    server = Server()
    server.server_program()