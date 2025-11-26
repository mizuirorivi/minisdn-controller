import socket
import struct

HOST = '0.0.0.0'
PORT = 6634 # default OpenFlow port

def recv_msg(conn):
    data = conn.recv(1024)
    print("[+]Recived Msg:",data.hex())
    return data

def of_hello():
    version = 0x01 # oldest and simplest OpenFlow version
    msg_type = 0x00 # OFPT_HELLO
    len = 8 # minimum message length
    xid = 1 # transaction ID
    
    # ! mean network byte order (big-endian)
    # B mean unsigned char (1 byte)
    # H mean unsigned short (2 bytes)
    # I mean unsigned int (4 bytes)
    return struct.pack('!BBH I', version, msg_type, len, xid)

def main():
    print("Hello from minisdn-controller!")
    
    # create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    print("[*]Listening on", HOST, PORT)
    conn, addr = s.accept()
    print("[*]Connected Addr", addr)
    
    # send hello message
    hello_msg = of_hello()
    conn.send(hello_msg)
    
    # receive message
    recv_msg(conn)
    
    # close connection
    conn.close()


if __name__ == "__main__":
    main()
