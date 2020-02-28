#
# PyQt5-based video-sync example for VLC Python bindings
# Copyright (C) 2009-2010 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#
"""
The client/server classes that keep multiple VLC python bindings players
synchronized.

Author: Saveliy Yusufov, Columbia University, sy2685@columbia.edu
Date: 25 January 2019
"""

import os
import platform
import socket
import sys
import struct
import threading
import logging
from concurrent import futures

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class Server:
    """Data sender server"""

    def __init__(self, host, port, data_queue):

        if platform.system() == "Windows":

            # Create a TCP/IP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to the port
            logger.info("Server started on %s port %s", host, port)
            self.sock.bind((host, port))

        else:
            server_address = "./uds_socket"

            # Make sure the socket does not already exist
            try:
                os.unlink(server_address)
            except OSError:
                if os.path.exists(server_address):
                    raise

            # Create a UDS socket
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

            # Bind the socket to the address
            logger.info("Server starting up on %s", server_address)
            self.sock.bind(server_address)

        # Listen for incoming connections
        self.sock.listen(5)

        self.clients = set()
        self.data_queue = data_queue
        listener_thread = threading.Thread(target=self.listen_for_clients, args=())
        listener_thread.daemon = True
        listener_thread.start()

    def listen_for_clients(self):
        logger.info("Now listening for clients")
        t = threading.Thread(target=self.data_sender, args=())
        t.daemon = True
        t.start()

        while True:
            client, _ = self.sock.accept()
            logger.info("Accepted Connection from: %s", client)
            self.clients.add(client)

    def data_sender(self):
        while True:
            data = self.data_queue.get()
            data = str(data).encode()
            msg = struct.pack(">I", len(data)) + data

            with futures.ThreadPoolExecutor(max_workers=5) as ex:
                for client in self.clients:
                    ex.submit(self.sendall, client, msg)

    def sendall(self, client, data):
        """Wraps socket module's `sendall` function"""
        try:
            client.sendall(data)
        except socket.error:
            logger.exception("Connection to client: %s was broken!", client)
            client.close()
            self.clients.remove(client)


class Client:
    """Data receiver client"""

    def __init__(self, address, port, data_queue):
        self.data_queue = data_queue

        if platform.system() == "Windows":

            # Create a TCP/IP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect the socket to the port where the server is listening
            logger.info("Connecting to %s port %s", address, port)
            self.sock.connect((address, port))
        else:

            # Create a UDS socket
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

            # Connect the socket to the port where the server is listening
            server_address = "./uds_socket"
            logger.info("New client connecting to %s", server_address)

            try:
                self.sock.connect(server_address)
            except socket.error:
                logger.exception()
                sys.exit(1)

        thread = threading.Thread(target=self.data_receiver, args=())
        thread.daemon = True
        thread.start()

    def recv_all(self, size):
        """Helper function to recv `size` number of bytes, or return False"""
        data = bytearray()

        while (len(data) < size):
            packet = self.sock.recv(size - len(data))
            if not packet:
                return False

            data.extend(packet)

        return data

    def recv_msg(self):
        """Receive the message size, n, and receive n bytes into a buffer"""
        raw_msg_size = self.recv_all(4)
        if not raw_msg_size:
            return False

        msg_size = struct.unpack(">I", raw_msg_size)[0]
        return self.recv_all(msg_size)

    def data_receiver(self):
        """Handles receiving, parsing, and queueing data"""
        logger.info("New data receiver thread started.")

        try:
            while True:
                raw_data = self.recv_msg()
                if raw_data:
                    data = raw_data.decode()
                    if 'd' in set(data):
                        self.data_queue.queue.clear()
                        continue
                    else:
                        self.data_queue.put(data)
        except:
            logger.exception("Closing socket: %s", self.sock)
            self.sock.close()
            return
