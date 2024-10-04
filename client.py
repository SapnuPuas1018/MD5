import os
import socket
import threading
import hashlib
from protocol import *

# BOMBOCLAT
IP = '127.0.0.1'
SERVER_PORT = 12345



class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread_list = []
        self.found = False
        self.lock = threading.Lock()
        self.num_cores = os.cpu_count()
        self.decrypted_msg = ''

    def start_client(self):
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

    def get_range(self):  # waiting for a command from the server to start
        range = recv(self.sock)
        print('range: ' + range)
        start, stop = range.split('-')
        start = int(start)
        stop = int(stop)
        return start, stop


    def decrypt(self, start, stop, sock, encrypted_msg):
        for i in range(start, stop):
            original = str(i).zfill(10)
            hash = self.md5(original)
            if hash == encrypted_msg:
                self.found = True
                print(f'found it : {original} ')
                send(sock, 'found')
                send(sock, str(original))


    def md5(self, str_to_hash):
        result = hashlib.md5(str_to_hash.encode())
        # print('The hexadecimal equivalent of hash is: ', end='')
        # print(result.hexdigest())
        return result.hexdigest()
