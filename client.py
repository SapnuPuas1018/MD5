import os
import socket
import threading
import hashlib
from protocol import *


SERVER_PORT = 12345
ENCRYPTED_MSG = 'ec9c0f7edcc18a98b1f31853b1813301' # 457694e29379be80d5dd65d3c519f15b     ec9c0f7edcc18a98b1f31853b1813301

found = False


def md5(str_to_hash):
    result = hashlib.md5(str_to_hash.encode())
    # print('The hexadecimal equivalent of hash is: ', end='')
    # print(result.hexdigest())
    return result.hexdigest()


def decrypt(start, stop, sock):
    global found
    for i in range(start, stop):
        original = str(i).zfill(10)
        hash = md5(original)
        if hash == ENCRYPTED_MSG:
            found = True
            print(f'found it : {original} ')
            send(sock, 'found')
            send(sock, str(original))


def get_range(sock):   # waiting for a command from the server to start
    range = recv(sock)
    print('range: ' + range)
    start, stop = range.split('-')
    start = int(start)
    stop = int(stop)
    return start, stop


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('127.0.0.1', SERVER_PORT))
        print('connected')

        # cpu cores
        num_cores = os.cpu_count()
        send(sock, str(num_cores))


        thread_list = []
        while not found:
            start_range, stop_range = get_range(sock)
            i = int((stop_range - start_range) / num_cores)
            for core in range(num_cores):
                start = start_range + i*core
                end = start_range + i*(core + 1)
                core_thread = threading.Thread(target=decrypt, args=(start, end, sock))
                core_thread.start()
                thread_list.append(core_thread)
                # print(thread_list)

            for thread in thread_list:
                thread.join()
                send(sock, 'not found')

            print(f'found : {found}')
    except socket.error as err:
        print('received socket error on client socket' + str(err))


if __name__ == '__main__':
    main()
