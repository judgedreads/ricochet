from socket import socket, AF_UNIX, SOCK_DGRAM
from gi.repository import GObject
import subprocess


class Server(object):

    def __init__(self, player):
        # create a named pipe for communication
        self.server = socket(AF_UNIX, SOCK_DGRAM)
        self.player = player
        try:
            self.server.bind('/tmp/ricochet')
        except OSError:
            subprocess.call(['rm', '/tmp/ricochet'])
            self.server.bind('/tmp/ricochet')

    # callback for the socket communication
    def handle_connection(self, source, condition):
        # receive data and decode it from bytes to str
        data = self.server.recv(1024).decode('UTF-8')
        if data == "toggle":
            self.player.toggle(None)
            message = "toggle"
        elif data == "next":
            self.player.skip_next(None)
            message = "next"
        elif data == "prev":
            self.player.skip_prev(None)
            message = "prev"
        # by returning True, the io watcher remains
        return True

    def main(self):
        GObject.io_add_watch(
            self.server, GObject.IO_IN, self.handle_connection)

    def close(self):
        self.server.close()
