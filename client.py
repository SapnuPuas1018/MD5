import os
import socket
import threading
import hashlib
from protocol import *

SERVER_PORT = 12345
MAX_PACKET = 1024


def md5(str_to_hash):
    result = hashlib.md5(str_to_hash.encode())

    print('The hexadecimal equivalent of hash is: ', end='')
    print(result.hexdigest())
    return result.hexdigest()


def decrypt(start, stop):
    for i in range(start, stop):
        hash = md5(str(i).zfill(10))
        if hash == 'EC9C0F7EDCC18A98B1F31853B1813301':
            print('found')


def wait_for_start():   # waiting for a command from the server to start
    pass


def main():

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.connect(('127.0.0.1', SERVER_PORT))
        print('connected')

        wait_for_start()

        num_cores = os.cpu_count()
        send(my_socket, str(num_cores))

        # receive range
        num_range = recv(my_socket) #   start-stop
        start, stop = num_range.split('-')
        i = int((stop - start)/num_cores)
        list = []
        for core in range(num_cores):
            core_thread = threading.Thread(target=decrypt, args=)

    except socket.error as err:
        print('received socket error on client socket' + str(err))


if __name__ == '__main__':
    main()
