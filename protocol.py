import socket


def send(connected_socket, msg):
    msg = msg.strip()

    msg = str(len(msg)) + '!' + ' '.join(msg.split())

    # Encode the modified 'msg' string and send it through the 'connected_socket'
    connected_socket.send(msg.encode())


def recv(connected_socket):
    length = ''
    while '!' not in length:
        length += connected_socket.recv(1).decode()
    length = length[:-1]

    length = int(length)

    # Receive the message until the expected length is reached
    received_msg = ''
    while len(received_msg) < length:
        received_msg += connected_socket.recv(length-len(received_msg)).decode()

    # Split the received message using '!!' as the separator
    return received_msg
