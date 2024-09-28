"""
The Python Class that implements the server
"""

import socket
import threading
from threading import Thread
import hashlib
from protocol import *

# Socket Constants
QUEUE_SIZE = 1
IP = '0.0.0.0'
PORT = 12345
SOCKET_TIMEOUT = 2

WORK_PER_CORE = 10**7
lock = threading.Lock()


class Server:
    def __init__(self):  # Use double underscores for the constructor
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread_list = []  # Initialize thread_list here
        self.found = False
        self.decrypted_str = ''
        self.last = 0

    def start_server(self):
        try:
            # Set up the server socket
            self.server_socket.bind((IP, PORT))
            self.server_socket.listen(QUEUE_SIZE)
            print("Listening for connections on port %d" % PORT)
            self.server_socket.settimeout(SOCKET_TIMEOUT)

            # Client Accepting Loop
            while not self.found:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print('New connection received from ' + addr[0] + ':' + str(addr[1]))

                    thread = Thread(target=self.handle_client, args=(client_socket, addr))  # Fix arguments
                    thread.start()
                    self.thread_list.append(thread)
                    print(self.found)
                except socket.timeout:
                    pass
        except socket.error as err:
            print('received socket exception - ' + str(err))
        finally:
            # Thread joining
            for thread in self.thread_list:
                thread.join()

            self.server_socket.close()
            return self.decrypted_str

    def handle_client(self, client_socket, addr):
        # Receive Work Request
        number_of_cores = recv(client_socket)
        print(f'number_of_cores: {number_of_cores}')
        while True:
            self.give_range(client_socket)
            data = recv(client_socket)
            if data == 'found':
                print('found it')
                self.decrypted_str = recv(client_socket)
                print('the original message is: ' + self.decrypted_str)

                self.found = True
                break

    def give_range(self, client_socket):
        lock.acquire()
        send(client_socket, f'{self.last}-{self.last + WORK_PER_CORE}')
        # print(f'i sent range: {self.last}-{self.last + WORK_PER_CORE}')
        self.last += WORK_PER_CORE
        lock.release()
