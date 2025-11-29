import unittest
from src.openflow import (
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
        result = packheader(OFPT_HELLO, 8, 1)
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
        result = make_hello()
        header, body = parseheader(result)

        self.assertEqual(header.msg_type, OFPT_HELLO)
        self.assertEqual(header.length, 8)
        self.assertEqual(body, b'')

    def test_make_features_request(self):
        """Test make_features_request creates valid Features Request message"""
        result = make_features_request()
        header, body = parseheader(result)

        self.assertEqual(header.msg_type, OFPT_FEATURES_REQUEST)
        self.assertEqual(header.length, 8)
        self.assertEqual(body, b'')


class TestDispatcher(unittest.TestCase):
    """Test cases for message dispatcher"""

    def test_dispatcher_hello(self):
        """Test dispatcher handles HELLO message"""
        # Should not raise exception
        dispatcher(OFPT_HELLO, b'')

    def test_dispatcher_features_reply(self):
        """Test dispatcher handles FEATURES_REPLY message"""
        # Should not raise exception
        dispatcher(OFPT_FEATURES_REPLY, b'')

    def test_dispatcher_packet_in(self):
        """Test dispatcher handles PACKET_IN message"""
        # Should not raise exception
        dispatcher(OFPT_PACKET_IN, b'')

    def test_dispatcher_unknown_message(self):
        """Test dispatcher handles unknown message type"""
        # Should not raise exception (logs error)
        dispatcher(255, b'')


if __name__ == '__main__':
    unittest.main()
