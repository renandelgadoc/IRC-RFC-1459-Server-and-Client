import socket
import threading

class User:

    def __init__(self, conn) -> None:

        self.conn = conn
        self.channel = None
        self.nickname = ""

class Server:

    def __init__(self) -> None:

        #channel name: channel instance
        self.channels = []

        # nickname: connection
        self.users = []
        
        self.instructions = {
            "PART": self.leave_channel,
            "NICK": self.change_nick,
            "QUIT": self.logout,
            "JOIN": self.join_channel,
            "LIST": self.list_channels
        }

    def validate_params(self, params, expected_number) -> bool:
        if len(params) != expected_number:
            return False
        return True
        
    def leave_channel(self, user, params) -> None:

        if not self.validate_params(params, expected_number = 1):
            raise Exception()

        data = user.nickname + " left the server"
        for a in self.users:
            if a.channel == user.channel:
                a.conn.send(data.encode())
        user.channel = None

        return

    def change_nick(self, user, params) -> str:

        if not self.validate_params(params, expected_number = 2):
            raise Exception()

        nickname = params[1]

        for a in self.users:
            if nickname == a.nickname:
                data = "ERR_NICKNAMEINUSE"
                user.conn.send(data.encode())
                return ""

        # First login
        if user.nickname == "":
            user.nickname = nickname
            print(nickname + " logged in")
            data = "Login successful"
            user.conn.send(data.encode())
            return nickname

        # Change nickname
        for a in self.users:
            data = "user changes nickname from " + user.nickname + " to " + nickname
            a.conn.send(data.encode())
        user.nickname = nickname
        data = "Login successful"
        user.conn.send(data.encode())

        return nickname

    def logout(self, user, params):
        user.conn.close()
        exit()
        
    def join_channel(self, user, params) -> None:

        if not self.validate_params(params, expected_number = 2):
            raise Exception()

        current_channel = params[1]

        # Add channel to self.channels if it doesn`t exist
        if current_channel not in self.channels:
            self.channels.append(current_channel)

        user.channel = current_channel
        data = "Connected to " + current_channel
        user.conn.send(data.encode())

        return


    def list_channels(self, nickname, conn, params):
        pass


    def thread_cliente(self, conn) -> None:

            user = User(conn)
            self.users.append(user)

            while True:
                try:
                    data = conn.recv(1024).decode()

                    # Remove space duplicates and split input in a list
                    data = " ".join(data.split(" "))
                    data = data.split(" ")

                    self.change_nick(user, data)

                    if user.nickname != "":
                        break
                except:
                    print("Error")
                    data = "Server Error"
                    conn.send(data.encode())


            while True:
                try:

                    # receive data stream. it won't accept data packet greater than 1024 bytes
                    data = conn.recv(1024).decode()
                    print(user.nickname + " sent " + data)

                    # Remove space duplicates and split input in a list
                    data = " ".join(data.split(" "))
                    data = data.split(" ")

                    # Check if the instruction is valid and call corresponding function
                    instruction = data[0]
                    if instruction in self.instructions:
                        self.instructions[data[0]](user, data)

                    # If the user is connected to a channel, sent message to all users in it
                    elif user.channel:
                        data =   "<" + user.nickname + "> " + " ".join(data)
                        for a in self.users:
                            if a.channel == user.channel:
                                a.conn.send(data.encode())
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