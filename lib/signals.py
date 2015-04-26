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
        sock = socket(AF_UNIX, SOCK_DGRAM)
        sock.connect('/tmp/ricochetctl')
        if data == "toggle":
            self.player.toggle(None)
            message = "toggle"
        elif data == "next":
            self.player.skip_next(None)
            message = "next"
        elif data == "prev":
            self.player.skip_prev(None)
            message = "prev"
        elif data == "pos":
            pos_min, pos_sec, dur_min, dur_sec = self.player.get_info(
                None, data)
            message = "%d:%d/%d:%d" % (pos_min, pos_sec, dur_min, dur_sec)
        elif data == "artist":
            message = self.player.get_info(None, data)
        elif data == "album":
            message = self.player.get_info(None, data)
        elif data == "song":
            message = self.player.get_info(None, data)

        info = bytes(message, 'UTF-8')
        sock.sendall(info)
        # by returning True, the io watcher remains
        return True

    def main(self):
        GObject.io_add_watch(
            self.server, GObject.IO_IN, self.handle_connection)

    def close(self):
        self.server.close()
