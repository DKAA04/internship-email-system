import unittest
from unittest.mock import patch, MagicMock
from email_handler import send_email

class TestEmailHandler(unittest.TestCase):
    @patch("email_handler.boto3.client")
    def test_send_email_success(self, mock_boto):
        mock_ses = MagicMock()
        mock_boto.return_value = mock_ses

        send_email("test@example.com", "Test", "This is a test", [])

        mock_ses.send_raw_email.assert_called_once()

if __name__ == "__main__":
    unittest.main()
