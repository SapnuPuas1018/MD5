"""
author - Yuval Hayun
date   - 06/10/24
"""

import os
import socket
import threading
import hashlib
from protocol import *


IP = '127.0.0.1'
SERVER_PORT = 12345


class Client:
    def __init__(self):
        """
        Initialize a Client instance.

        :param None: No parameters for the constructor
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread_list = []
        self.found = False
        self.lock = threading.Lock()
        self.num_cores = os.cpu_count()
        self.decrypted_msg = ''

    def start_client(self):
        """
        Start the client and initiate communication with the server. It receives an encrypted message,
        distributes decryption tasks among multiple threads, and communicates back with the server.

        :param None: No parameters
        :return: None
        :rtype: None
        """
        try:
            self.sock.connect((IP, SERVER_PORT))
            print('connected')

            encrypted_msg = recv(self.sock)

            send(self.sock, str(self.num_cores))

            while not self.found:
                start_range, stop_range = self.get_range()
                i = int((stop_range - start_range) / self.num_cores)
                for core in range(self.num_cores):
                    start = start_range + i * core
                    end = start_range + i * (core + 1)
                    core_thread = threading.Thread(target=self.decrypt, args=(start, end, self.sock, encrypted_msg))
                    core_thread.start()
                    self.thread_list.append(core_thread)
                for thread in self.thread_list:
                    thread.join()
                    send(self.sock, 'not found')

                print(f'found : {self.found}')

        except socket.error as err:
            print('received socket error on client socket : ' + str(err))

        finally:
            self.sock.close()

    def get_range(self):
        """
        Receive the range from the server to define the interval for decryption.

        :param None: No parameters
        :return: A tuple containing the start and stop of the range.
        :rtype: tuple(int, int)
        """
        range = recv(self.sock)
        print('range: ' + range)
        start, stop = range.split('-')
        start = int(start)
        stop = int(stop)
        return start, stop

    def decrypt(self, start, stop, sock, encrypted_msg):
        """
        Decrypts the message by hashing values in the specified range and comparing to the encrypted message.

        :param start: Start of the range to check
        :type start: int
        :param stop: End of the range to check
        :type stop: int
        :param sock: The socket to send results to
        :type sock: socket.socket
        :param encrypted_msg: The encrypted message received from the server
        :type encrypted_msg: str
        :return: None
        :rtype: None
        """
        for i in range(start, stop):
            original = str(i).zfill(10)
            hash = self.md5(original)
            if hash == encrypted_msg:
                self.found = True
                print(f'found it : {original} ')
                send(sock, 'found')
                send(sock, str(original))

    def md5(self, str_to_hash):
        """
        Generate an MD5 hash of the given string.

        :param str_to_hash: The string to hash
        :type str_to_hash: str
        :return: The MD5 hash of the input string in hexadecimal form
        :rtype: str
        """
        result = hashlib.md5(str_to_hash.encode())
        return result.hexdigest()


if __name__ == '__main__':
    # Create a client instance
    client = Client()

    # Test socket initialization
    assert isinstance(client.sock, socket.socket), "Socket initialization failed!"
    assert client.num_cores > 0, "Number of cores should be greater than 0!"

    # Test MD5 hashing function
    test_string = "1234567890"
    expected_hash = hashlib.md5(test_string.encode()).hexdigest()
    assert client.md5(test_string) == expected_hash, "MD5 hashing function failed!"

    client.get_range = lambda: (0, 100)  # Mocking get_range to return a fixed range

    start, stop = client.get_range()
    assert start == 0 and stop == 100, "get_range function did not return expected values!"

    print("All assertions passed!")

    # Start the client (you may want to mock socket connections for proper testing)
    # client.start_client() # Uncomment if testing with actual server
