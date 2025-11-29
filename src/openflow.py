from src.log import success, error
from dataclasses import dataclass
import struct
# Message types
OFPT_HELLO            = 0
OFPT_ERROR            = 1
OFPT_ECHO_REQUEST     = 2
OFPT_ECHO_REPLY       = 3
OFPT_FEATURES_REQUEST = 5
OFPT_FEATURES_REPLY   = 6
OFPT_PACKET_IN        = 10
OFPT_FLOW_MOD         = 14

@dataclass
class OFHeader:
    version: int
    msg_type: int
    length: int
    xid: int

def packheader(msg_type, length, xid, version=0x01):
    # ! mean network byte order (big-endian)
    # B mean unsigned char (1 byte)
    # H mean unsigned short (2 bytes)
    # I mean unsigned int (4 bytes)
    return struct.pack('!BBH I', version, msg_type, length, xid)
def parseheader(data):
    version, msg_type, length, xid = struct.unpack("!BBHI", data[:8])
    body = data[8:]
    return OFHeader(version, msg_type, length, xid),body

def make_hello():
    return packheader(OFPT_HELLO, 8, 1)

def make_features_request():
    return packheader(OFPT_FEATURES_REQUEST, 8, 1)




def handler_hello(data):
    success("Hello message received")
def handler_features_reply(data):
    success("Features reply message received")
def handler_packet_in(data):
    success("Packet in message received")
    
handlers = {
        0:  handler_hello,
        6:  handler_features_reply,
        10: handler_packet_in,
}


def dispatcher(msg_type, data):
    fn = handlers.get(msg_type)
    if fn:
        fn(data)
    else:
        error("Unknown message type: " + str(msg_type))