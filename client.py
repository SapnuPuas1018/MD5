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


def decrypt(start, stop, sock):
    for i in range(start, stop):
        hash = md5(str(i).zfill(10))
        if hash == 'EC9C0F7EDCC18A98B1F31853B1813301':
            print('found')
            send(sock, 'found')



def wait_for_start():   # waiting for a command from the server to start
    pass


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('127.0.0.1', SERVER_PORT))
        print('connected')

        wait_for_start()

        num_cores = os.cpu_count()
        send(sock, str(num_cores))
        #
        # # receive range
        # num_range = recv(sock) #   start-stop
        # start, stop = num_range.split('-')
        start_range = 0
        stop_range = 1000000000
        i = int((stop_range - start_range)/num_cores)
        thread_list = []
        for core in range(num_cores):
            start = start_range + i*core
            end = start_range + i*(core + 1)
            core_thread = threading.Thread(target=decrypt, args=(start, end, sock))
            thread_list.append(core_thread)
            print(thread_list)

    except socket.error as err:
        print('received socket error on client socket' + str(err))


if __name__ == '__main__':
    main()
