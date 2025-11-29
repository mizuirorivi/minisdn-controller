import unittest
from unittest.mock import Mock, patch, MagicMock
from src.controller import Controller


class TestController(unittest.TestCase):
    """Test cases for Controller class"""

    def setUp(self):
        """Set up test fixtures"""
        self.controller = Controller(host='127.0.0.1', port=6634)

    def test_init(self):
        """Test Controller initialization"""
        self.assertEqual(self.controller.host, '127.0.0.1')
        self.assertEqual(self.controller.port, 6634)

    def test_init_default_values(self):
        """Test Controller initialization with default values"""
        controller = Controller()
        self.assertEqual(controller.host, '0.0.0.0')
        self.assertEqual(controller.port, 6634)

    @patch('src.controller.socket.socket')
    def test_start_creates_socket(self, mock_socket):
        """Test that start() creates and configures a socket"""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        mock_sock.accept.return_value = (MagicMock(), ('127.0.0.1', 12345))

        with patch.object(self.controller, 'handle_connection'):
            self.controller.start()

        mock_socket.assert_called_once()
        mock_sock.bind.assert_called_once_with(('127.0.0.1', 6634))
        mock_sock.listen.assert_called_once_with(1)

    def test_recv_msg(self):
        """Test recv_msg receives data from connection"""
        mock_conn = MagicMock()
        test_data = b'\x01\x00\x00\x08\x00\x00\x00\x01'
        mock_conn.recv.return_value = test_data

        result = self.controller.recv_msg(mock_conn)

        self.assertEqual(result, test_data)
        mock_conn.recv.assert_called_once_with(1024)


if __name__ == '__main__':
    unittest.main()
