import unittest
from unittest.mock import patch
from io import StringIO
from src.utils.log import info, success, error, debug


class TestLogFunctions(unittest.TestCase):
    """Test cases for logging functions"""

    @patch('sys.stdout', new_callable=StringIO)
    def test_info(self, mock_stdout):
        """Test info function prints with [*] prefix"""
        info("test message")
        output = mock_stdout.getvalue()
        self.assertEqual(output, "[*] test message\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_success(self, mock_stdout):
        """Test success function prints with [+] prefix"""
        success("test message")
        output = mock_stdout.getvalue()
        self.assertEqual(output, "[+] test message\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_error(self, mock_stdout):
        """Test error function prints with [!] prefix"""
        error("test message")
        output = mock_stdout.getvalue()
        self.assertEqual(output, "[!] test message\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_debug(self, mock_stdout):
        """Test debug function prints with [?] prefix"""
        debug("test message")
        output = mock_stdout.getvalue()
        self.assertEqual(output, "[?] test message\n")

    @patch('sys.stdout', new_callable=StringIO)
    def test_info_with_formatting(self, mock_stdout):
        """Test info function with formatted string"""
        info(f"Connection from {'127.0.0.1'}")
        output = mock_stdout.getvalue()
        self.assertEqual(output, "[*] Connection from 127.0.0.1\n")


if __name__ == '__main__':
    unittest.main()
