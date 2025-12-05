from src.openflow import make_hello, make_features_request, parseheader, dispatcher
import socket

from src.log import info, success, error, debug

class Controller:
    def __init__(self, host='0.0.0.0', port=6634):
        self.host = host
        self.port = port
        self.xid = 1
    def next_xid(self):
        self.xid += 1
        return self.xid
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
            conn.send(make_hello(self.next_xid()))
            success("Send Hello Message")
            # send features request message
            conn.send(make_features_request(self.next_xid()))
            success("Send Features Request Message")
            # -- end of handshake --
            
            # -- message loop --
            while True:
                data = self.recv_msg(conn)
                if not data:
                    # Connection closed
                    break
                hdr,body = parseheader(data)

                dispatcher(conn,hdr,body)

            # -- end of message loop --
        except Exception as e:
            error(f"Error handling connection: {e}")
        finally:
            # close connection
            conn.close()
    def recv_msg(self, conn):
        data = conn.recv(1024)
        if data:
            success(f"Recived Msg: {data.hex()}")
        else:
            # Empty data means the connection was closed
            info("Connection closed by client")
        return data
