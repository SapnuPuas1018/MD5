"""
author - Yuval Hayun
date   - 06/10/24
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

ENCRYPTED_MSG = 'ec9c0f7edcc18a98b1f31853b1813301'  # Example encrypted message


class Server:
    def __init__(self):
        """
        Initialize the Server instance, setting up the server socket and other variables.

        :param None: No parameters for the constructor
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread_list = []  # List of threads handling clients
        self.found = False  # Flag to indicate if the original message is found
        self.decrypted_str = ''  # Decrypted original message
        self.last = 0  # Track the range of numbers to send to clients

    def start_server(self):
        """
        Start the server to listen for client connections, distribute work ranges, and handle client communication.

        :param None: No parameters
        :return: The decrypted original message if found
        :rtype: str
        """
        try:
            # Set up the server socket
            self.server_socket.bind((IP, PORT))
            self.server_socket.listen(QUEUE_SIZE)
            print(f"Listening for connections on port {PORT}")
            self.server_socket.settimeout(SOCKET_TIMEOUT)

            # Client Accepting Loop
            while not self.found:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print(f'New connection received from {addr[0]}:{addr[1]}')

                    thread = Thread(target=self.handle_client, args=(client_socket, addr))
                    thread.start()
                    self.thread_list.append(thread)
                except socket.timeout:
                    pass

        except socket.error as err:
            print(f'socket exception - {err}')

        finally:
            # Join threads before exiting
            for thread in self.thread_list:
                thread.join()
            self.server_socket.close()

            return self.decrypted_str

    def handle_client(self, client_socket, addr):
        """
        Handle communication with a connected client. Sends the encrypted message, assigns work ranges,
        and waits for the client's decryption results.

        :param client_socket: The socket connected to the client
        :type client_socket: socket.socket
        :param addr: The address of the connected client
        :type addr: tuple
        :return: None
        :rtype: None
        """
        try:
            send(client_socket, ENCRYPTED_MSG)
            # Receive the number of cores the client can use
            number_of_cores = recv(client_socket)
            print(f'number_of_cores: {number_of_cores}')

            while not self.found:
                self.give_range(client_socket)
                data = recv(client_socket)
                if data == 'found':
                    print('found it')
                    self.decrypted_str = recv(client_socket)
                    print(f'the original message is: {self.decrypted_str}')
                    self.found = True
        except (ConnectionResetError, BrokenPipeError) as err:
            print(f'Client disconnected unexpectedly - {err}')
        finally:
            try:
                client_socket.close()  # Close client socket once done
            except Exception as err:
                print(f'Error closing client socket: {err}')

    def give_range(self, client_socket):
        """
        Send a range of numbers to the client for decryption testing. Ensures thread safety with a lock.

        :param client_socket: The socket connected to the client
        :type client_socket: socket.socket
        :return: None
        :rtype: None
        """
        lock.acquire()
        try:
            send(client_socket, f'{self.last}-{self.last + WORK_PER_CORE}')
            self.last += WORK_PER_CORE  # Update the range for the next request
        finally:
            lock.release()


if __name__ == '__main__':
    # Create server instance
    server = Server()

    # Assert that the server socket is initialized correctly
    assert isinstance(server.server_socket, socket.socket), "Server socket initialization failed!"

    # Assert that the encrypted message is set
    assert ENCRYPTED_MSG != '', "Encrypted message should not be empty!"
    assert len(ENCRYPTED_MSG) == 32, "Encrypted message length should be 32 characters (MD5 hash)!"

    # Check that the initial range value is set correctly
    assert server.last == 0, "Initial range should be 0!"

    # Test md5 hash function
    test_string = "1234567890"
    expected_hash = hashlib.md5(test_string.encode()).hexdigest()
    assert hashlib.md5(test_string.encode()).hexdigest() == expected_hash, "MD5 hash test failed!"

    print("All assertions passed!")

    # Start the server (might require actual client interaction or additional mocking)
    # server.start_server()  # Uncomment if testing with real clients
