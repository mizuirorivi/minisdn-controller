@dataclass
class OFActionOutput:
    type: int
    len: int
    port: int
    max_len: int

def pack_action_output(action: OFActionOutput):
    return struct.pack("!HHHI", action.type, action.len, action.port, action.max_len)