import unittest
from unittest.mock import MagicMock
from src.openflow.openflow import (
    OFHeader,
    packheader,
    parseheader,
    make_hello,
    make_features_request,
    dispatcher,
    OFPT_HELLO,
    OFPT_FEATURES_REQUEST,
    OFPT_FEATURES_REPLY,
    OFPT_PACKET_IN,
    OFPT_ECHO_REQUEST,
)


class TestOFHeader(unittest.TestCase):
    """Test cases for OFHeader dataclass"""

    def test_ofheader_creation(self):
        """Test OFHeader creation"""
        header = OFHeader(version=1, msg_type=0, length=8, xid=1)
        self.assertEqual(header.version, 1)
        self.assertEqual(header.msg_type, 0)
        self.assertEqual(header.length, 8)
        self.assertEqual(header.xid, 1)


class TestHeaderPacking(unittest.TestCase):
    """Test cases for header packing and parsing"""

    def test_packheader(self):
        """Test packheader creates correct binary format"""
        result = packheader(OFPT_HELLO, 8, 1, version=0x01)
        # Expected: version=0x01, type=0, length=8, xid=1
        expected = b'\x01\x00\x00\x08\x00\x00\x00\x01'
        self.assertEqual(result, expected)

    def test_parseheader(self):
        """Test parseheader correctly parses binary data"""
        data = b'\x01\x00\x00\x08\x00\x00\x00\x01'
        header, body = parseheader(data)

        self.assertEqual(header.version, 1)
        self.assertEqual(header.msg_type, 0)
        self.assertEqual(header.length, 8)
        self.assertEqual(header.xid, 1)
        self.assertEqual(body, b'')

    def test_parseheader_with_body(self):
        """Test parseheader with message body"""
        data = b'\x01\x00\x00\x0c\x00\x00\x00\x01TEST'
        header, body = parseheader(data)

        self.assertEqual(header.length, 12)
        self.assertEqual(body, b'TEST')


class TestMessageCreation(unittest.TestCase):
    """Test cases for OpenFlow message creation"""

    def test_make_hello(self):
        """Test make_hello creates valid Hello message"""
        result = make_hello(xid=1)
        # Parse directly without using parseheader since HELLO is sent by controller
        import struct
        version, msg_type, length, xid = struct.unpack("!BBHI", result[:8])

        self.assertEqual(version, 0x01)
        self.assertEqual(msg_type, OFPT_HELLO)
        self.assertEqual(length, 8)
        self.assertEqual(xid, 1)

    def test_make_features_request(self):
        """Test make_features_request creates valid Features Request message"""
        result = make_features_request(xid=1)
        # Parse directly without using parseheader since FEATURES_REQUEST is sent by controller
        import struct
        version, msg_type, length, xid = struct.unpack("!BBHI", result[:8])

        self.assertEqual(version, 0x01)
        self.assertEqual(msg_type, OFPT_FEATURES_REQUEST)
        self.assertEqual(length, 8)
        self.assertEqual(xid, 1)


class TestDispatcher(unittest.TestCase):
    """Test cases for message dispatcher"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_ctrl = MagicMock()
        self.mock_conn = MagicMock()

    def test_dispatcher_hello(self):
        """Test dispatcher handles HELLO message"""
        header = OFHeader(version=1, msg_type=OFPT_HELLO, length=8, xid=1)
        # Should not raise exception
        dispatcher(self.mock_ctrl, self.mock_conn, header, b'')

    def test_dispatcher_features_reply(self):
        """Test dispatcher handles FEATURES_REPLY message"""
        header = OFHeader(version=1, msg_type=OFPT_FEATURES_REPLY, length=32, xid=1)
        # Create minimal features reply body (24 bytes minimum)
        body = b'\x00' * 24
        # Should not raise exception
        dispatcher(self.mock_ctrl, self.mock_conn, header, body)

    def test_dispatcher_echo_request(self):
        """Test dispatcher handles ECHO_REQUEST message"""
        header = OFHeader(version=1, msg_type=OFPT_ECHO_REQUEST, length=8, xid=1)
        # Should not raise exception
        dispatcher(self.mock_ctrl, self.mock_conn, header, b'')
        # Verify echo reply was sent
        self.mock_conn.send.assert_called_once()


if __name__ == '__main__':
    unittest.main()
