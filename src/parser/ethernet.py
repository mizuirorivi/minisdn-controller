from scapy.all import Ether

def parse_ethernet(raw: bytes):
    """
    Parse raw Ethernet frame using Scapy and return a Scapy Ether object.
    """
    try:
        eth = Ether(raw)
        return eth
    except Exception as e:
        raise ValueError(f"Failed to parse Ethernet frame: {e}")