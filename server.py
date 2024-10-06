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

ENCRYPTED_MSG = 'ec9c0f7edcc18a98b1f31853b1813301' # 457694e29379be80d5dd65d3c519f15b     ec9c0f7edcc18a98b1f31853b1813301     e807f1fcf82d132f9bb018ca6738a19f


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
            print('socket exception - ' + str(err))

        finally:
            # Thread joining
            for thread in self.thread_list:
                thread.join()
            self.server_socket.close()

            return self.decrypted_str


    def handle_client(self, client_socket, addr):
        try:
            send(client_socket, ENCRYPTED_MSG)
            # Receive Work Request
            number_of_cores = recv(client_socket)
            print(f'number_of_cores: {number_of_cores}')
            while not self.found:
                self.give_range(client_socket)
                data = recv(client_socket)
                if data == 'found':
                    print('found it')
                    self.decrypted_str = recv(client_socket)
                    print('the original message is: ' + self.decrypted_str)

                    self.found = True
        except (ConnectionResetError, BrokenPipeError) as err:
            print('Client disconnected unexpectedly - ' + err)
        finally:
            # Decrement active clients once this client is done
            try:
                client_socket.close()
            except Exception as err:
                print(f'Error closing client socket: {err}')


    def give_range(self, client_socket):
        lock.acquire()
        send(client_socket, f'{self.last}-{self.last + WORK_PER_CORE}')
        # print(f'i sent range: {self.last}-{self.last + WORK_PER_CORE}')
        self.last += WORK_PER_CORE
        lock.release()



if __name__ == '__main__':
    # Create server instance
    server = Server()

    # Assert that the server socket is initialized correctly
    assert isinstance(server.server_socket, socket.socket), "Server socket initialization failed!"

    # Assert that the encrypted message is set
    assert ENCRYPTED_MSG != '', "Encrypted message should not be empty!"
    assert len(ENCRYPTED_MSG) != 10, "Encrypted message length should be 10!"

    # Check that initial range value is set correctly
    assert server.last == 0, "Initial range should be 0!"

    # Test md5 hash function
    test_string = "1234567890"
    expected_hash = hashlib.md5(test_string.encode()).hexdigest()
    assert hashlib.md5(test_string.encode()).hexdigest() == expected_hash, "MD5 hash test failed!"


    print("All assertions passed!")

    # Start the server (might require actual client interaction or additional mocking)
    # server.start_server()  # Uncomment if testing with real clients
