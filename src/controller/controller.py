from src.openflow.openflow import make_hello, make_features_request, parseheader, dispatcher
from src.controller.state.mac_table import MACLearningTable
import socket
import struct

from src.utils.log import info, success, error, debug

class Controller:
    def __init__(self, host='0.0.0.0', port=6634):
        self.host = host
        self.port = port
        self.xid = 1
        self.mac_table: MACLearningTable = MACLearningTable()

    def next_xid(self):
        self.xid += 1
        return self.xid

    def _recv_exact(self, conn, nbytes):
        """Receive exactly nbytes from the socket, or return None if closed."""
        data = b''
        while len(data) < nbytes:
            chunk = conn.recv(nbytes - len(data))
            if not chunk:
                return None
            data += chunk
        return data

    def recv_msg(self, conn):
        """Receive a full OpenFlow message (header + body)."""
        header = self._recv_exact(conn, 8)
        if not header:
            return None

        try:
            version, msg_type, length, xid = struct.unpack("!BBHI", header)
        except struct.error as e:
            error(f"Error unpacking header: {e}")
            return None

        if length < 8:
            error(f"Invalid message length: {length}")
            return None

        body = b''
        remaining = length - 8
        if remaining > 0:
            body = self._recv_exact(conn, remaining)
            if body is None:
                return None

        return header + body

    def start(self):
        # create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)
        info(f"Listening on {self.host} {self.port}")

        # accept connections in a loop
        while True:
            try:
                client_sock, client_addr = s.accept()
                info(f"Connection from {client_addr}")
                self.handle_connection(client_sock)
            except KeyboardInterrupt:
                info("Shutting down controller...")
                break
            except Exception as e:
                error(f"Error accepting connection: {e}")

        s.close()

    def handle_connection(self, conn):
        try:
            # -- handshake --
            # send hello message
            hello_xid = self.next_xid()
            conn.send(make_hello(hello_xid))
            success(f"Send Hello Message (xid = {hello_xid})")
            # send features request message
            features_xid = self.next_xid()
            conn.send(make_features_request(features_xid))
            success(f"Send Features Request Message (xid = {features_xid})")
            # -- end of handshake --
            # -- message loop --
            while True:
                msg = self.recv_msg(conn)
                if not msg:
                    break
                try:
                    hdr, body = parseheader(msg)
                except ValueError as e:
                    error(f"Error parsing header: {e}")
                    break
                dispatcher(self,conn, hdr, body)


            # -- end of message loop --
        except Exception as e:
            import traceback
            traceback.print_exc()
            error(f"Error handling connection: {e}")
        finally:
            # close connection
            conn.close()
