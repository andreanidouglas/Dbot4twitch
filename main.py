import socket
import time
import random
import threading

cmtedouglas_access_token = ''


def generate_random_string():
    size = random.randint(10, 150)
    _string = ""
    for i in range(size):
        _string += chr(random.randint(65, 90))

    return _string.lower()


def chat_connect():
    HOST = 'irc.twitch.tv'
    PORT = 6667

    password = 'oauth:'+cmtedouglas_access_token
    nick = 'cmtedouglas'
    bot_owner = 'cmtedouglas'
    channel = '#cmtedouglas'

    readbuffer = ""

    s = socket.socket()
    s.settimeout(2)
    s.connect((HOST, PORT))

    s.send(bytes("PASS {}\r\n".format(password), 'utf-8'))
    s.send(bytes('USER {} 0 * :{}\r\n'.format(nick, bot_owner), "utf-8"))
    s.send(bytes('NICK {}\r\n'.format(nick), "utf-8"))

    readbuffer = s.recv(1024)
    print(readbuffer.decode('utf8'))
    s.send(bytes('JOIN {}\r\n'.format(channel), "utf-8"))
    s.send(bytes("PRIVMSG {} : {} \r\n".format(channel, 'voila'), "utf-8"))
    return s


class _socket:
    def __init__(self, operation, s_socket, start=0):
        self.lock = threading.Lock()
        self.value = start
        self.operation = operation
        self.socket = s_socket

    def operete(self):
        self.lock.acquire()
        try:
            print(self.operation.name + ' acquired lock\n')
            self.operation.do(self.socket)
            self.value = self.value+1
        finally:
            self.lock.release()
            self.operation.sleep()


class _operation:
    def __init__(self, name):
        self.name = name

    def do(self, sock):
        self.name = 'Invalid'

    def sleep(self):
        time.sleep(10)


class receive(_operation):
    _buffer = None

    def do(self, sock):
        try:
            self._buffer = sock.recv(1024)
            print(self._buffer.decode('utf8'))
            if self._buffer.decode('utf8').find('PING') == 0:
                print('enviando pong')
                sock.send(bytes(("PONG :tmi.twitch.tv"), 'UTF8'))
        except socket.timeout:
            print('nenhuma mensagem recebida')

    def get_buffer(self):
        return self._buffer

    def get_message(self):
        decoded_buffer = self._buffer.decode('utf8').split(":")
        print(decoded_buffer[len(decoded_buffer)])
        return str(decoded_buffer[len(decoded_buffer)])


class send(_operation):
    _message = None
    _channel = None

    def sleep(self):
        sleep_time = random.randint(60, 180)
        time.sleep(sleep_time)

    def set_channel(self, channel):
        self._channel = channel

    def do(self, sock):
        self.message = generate_random_string()
        sock.send(bytes("PRIVMSG {} : {} \r\n".format(
            self._channel,
            generate_random_string()), "utf-8"))


def worker(object):
    s = chat_connect()
    socket_lock = None
    if isinstance(object, send):
        sendO = send("Send")
        sendO.set_channel("#cmtedouglas")
        socket_lock = _socket(sendO, s)
    else:
        recO = receive("Receive")
        socket_lock = _socket(recO, s)
    while 1:
        socket_lock.operete()


if __name__ == "__main__":
    sendO = send("Send")
    recO = receive("Receive")

    t = threading.Thread(target=worker, args=(sendO,))
    t.start()
    t1 = threading.Thread(target=worker, args=(recO,))
    t1.start()
