import socket
import threading

def handle_client(client_socket):
    while True:
        data = client_socket.recv(64).decode()
        if not data:
            break
        print('Received from client: ' + data)
        message = input(" -> ")  # take input from server
        client_socket.send(message.encode())  # send message
    client_socket.close()

def server_program():
    host = "0.0.0.0"  # as both code is running on same pc
    port = 5000  # socket server port number

    server_socket = socket.socket()  # get instance
    server_socket.bind((host, port))  # bind host address and port together

    server_socket.listen(5)  # configure how many clients the server can listen simultaneously
    print("Server listening on port " + str(port))

    while True:
        client_socket, addr = server_socket.accept()  # establish a connection with client
        print('Got a connection from %s' % str(addr))
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    server_program()
