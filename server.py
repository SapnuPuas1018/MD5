import logging
import socket
import threading
from protocol import *

IP = '127.0.0.1'
PORT = 12345
QUEUE_LEN = 20
MAX_PACKET = 1024

def give_range():
    pass

def handle_client(client_socket, client_address):
    number_of_cores = recv(client_socket)
    print(f'number_of_cores: {number_of_cores}')
    give_range()
    recv(client_socket)


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_LEN)
        print("Listening for connections on port %d" % PORT)

        thread_list = []
        while len(thread_list) != 1:
            client_socket, client_address = server_socket.accept()
            print('New connection received from ' + client_address[0] + ':' + str(client_address[1]))

            thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.start()
            thread_list.append(thread)
            print(thread_list)

        print('done')
    except socket.error as err:
        print('received socket error on client socket' + str(err))

    finally:
        server_socket.close()


if __name__ == '__main__':
    main()
