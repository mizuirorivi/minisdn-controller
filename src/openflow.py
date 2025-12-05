from src.log import success, error,info
from dataclasses import dataclass
import struct
from typing import List
# see official openflow 1.0 spec(https://opennetworking.org/wp-content/uploads/2013/04/openflow-spec-v1.0.0.pdf)
# see openflow switch spec(https://opennetworking.org/wp-content/uploads/2014/10/openflow-spec-v1.1.0.pdf)

# Message types enum ofp_type (in official openflow spec 18p)
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

@dataclass
class OFPhyPort:
    port_no: int
    hw_addr: bytes
    name: str
    config: int
    state: int
    curr: int
    advertised: int
    supported: int
    peer: int

@dataclass 
class OFFeaturesReply:
    datapath_id: int
    n_buffers: int
    n_tables: int
    capabilities: int
    actions: int
    ports: List["OFPhyPort"]

def packheader(msg_type, length, xid, version=0x01):
    # ! mean network byte order (big-endian)
    # B mean unsigned char (1 byte)
    # H mean unsigned short (2 bytes)
    # I mean unsigned int (4 bytes)
    # see https://docs.python.org/3/library/struct.html
    return struct.pack('!BBHI', version, msg_type, length, xid)

def parseheader(data):
    # parse header
    version, msg_type, length, xid = struct.unpack("!BBHI", data[:8])
    body = data[8:length]
    assert version == 0x01, "Unsupported OpenFlow version: " + str(version)
    assert msg_type in handlers, "Unknown message type: " + str(msg_type)
    assert length >= 8, "Invalid message length: " + str(length)
    assert xid >= 0, "Invalid xid: " + str(xid)
    return OFHeader(version, msg_type, length, xid),body

def parse_phy_port(raw: bytes) -> OFPhyPort:
    """
    port_no: 2 bytes
    hw_addr: 6 bytes; uint8_t hw_addr[OFP_ETH_ALEN=6] mac address 
    name: 16 bytes; char name[OFP_MAX_PORT_NAME_LEN=16]
    config: 4 bytes
    state: 4 bytes

    <Bitmaps of OFPPF_* that describe features. All bits zeroed if
    unsupported or unavailable>
    curr: 4 bytes
    advertised: 4 bytes
    supported: 4 bytes
    peer: 4 bytes
    """
    port_no, = struct.unpack("!H", raw[0:2])
    hw_addr = raw[2:8]
    hw_addr = ":".join(f"{byte:02x}" for byte in hw_addr)
    info(f"Port hw_addr: {hw_addr}")
    name = raw[8:24].split(b'\x00', 1)[0].decode("ascii", errors="ignore")
    info(f"Port name: {name}")
    config, state, curr, adv, supp, peer = struct.unpack("!IIIIII", raw[24:48])
    info(f"Port config: {config}, state: {state}, curr: {curr}, adv: {adv}, supp: {supp}, peer: {peer}")
    return OFPhyPort(
        port_no=port_no,
        hw_addr=hw_addr,
        name=name,
        config=config,
        state=state,
        curr=curr,
        advertised=adv,
        supported=supp,
        peer=peer,
    )

def parse_phy_ports(raw_ports: bytes) -> List[OFPhyPort]:
    """
    raw_ports: port part of feature reply(body[24:])

    ofp_phy_port is 48 byte(openflow 1.0)
    """
    PORT_SIZE = 48
    ports = []
    len_ports = len(raw_ports) // PORT_SIZE
    if(len_ports != 0):
        error("Invalid port block length")
    
    info(f"number of ports: {len_ports}")
    ports = [parse_phy_port(raw_ports[i:i + PORT_SIZE]) for i in range(0, len(raw_ports), PORT_SIZE)]
    return ports


def parse_features_reply(body):
    """
    datapath_id: 8 bytes
    n_buffers: 4 bytes
    n_tables: 1 bytes
    pad: 3 bytes
    capabilities: 4 bytes
    actions: 4 bytes
    ports: variable length
    """

    if len(body) < 24:
        error(f"Features reply too short: {len(body)} bytes")
        raise ValueError("Features reply body too short")

    offset = 0
    
    datapath_id, n_buffers, n_tables = struct.unpack("!QIB", body[offset:offset+13])
    offset += 13
    # pad is 3 bytes for aligiment
    # thats why it is skipped
    offset += 3
    capabilities, actions = struct.unpack("!II", body[offset:offset+8])
    offset += 8
    assert offset == 24
    

    ports = parse_phy_ports(body[offset:])
    info(
    "Features reply: "
    f"datapath_id=0x{datapath_id:016x}, "
    f"n_buffers={n_buffers}, "
    f"n_tables={n_tables}, "
    f"capabilities=0x{capabilities:08x}, "
    f"actions=0x{actions:08x}, "
    f"num_ports={len(ports)}"
    )

    return OFFeaturesReply(datapath_id, n_buffers, n_tables, capabilities, actions, ports)


def make_hello(xid):
    return packheader(OFPT_HELLO, 8, xid)

def make_echo_reply(hdr):
    return packheader(OFPT_ECHO_REPLY, hdr.length, hdr.xid)
    
def make_features_request(xid):
    return packheader(OFPT_FEATURES_REQUEST, 8, xid)


def handler_hello(conn,hdr,body):
    success(f"Hello message received(xid = {hdr.xid})")
def handler_echo_request(conn,hdr,body):
    success(f"Echo request message received(xid = {hdr.xid})")
    reply =  make_echo_reply(hdr)
    conn.send(reply)
    success(f"Echo reply message sent(xid = {hdr.xid})")
def handler_features_reply(conn,hdr,body):
    success(f"Features reply message received(xid = {hdr.xid})")
    parse_features_reply(body)
def handler_packet_in(conn,hdr,body):
    success(f"Packet in message received(xid = {hdr.xid})")
    
handlers = {
        OFPT_HELLO:  handler_hello,
        OFPT_FEATURES_REPLY:  handler_features_reply,
        OFPT_PACKET_IN: handler_packet_in,
        OFPT_ECHO_REQUEST: handler_echo_request,
}


def dispatcher(conn,hdr,body):
    assert hdr.msg_type in handlers, "Unknown message type: " + str(hdr.msg_type)
    fn = handlers.get(hdr.msg_type)
    assert fn is not None, "Unknown message type: " + str(hdr.msg_type)
    fn(conn,hdr,body)
    