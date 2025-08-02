import os
import unittest
import tempfile
from server import app

class CoolSpaceBackendTestCase(unittest.TestCase):
    """Test case for the CoolSpace AI backend server."""

    def setUp(self):
        """Set up a test client and configure the app for testing."""
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
        self.client = app.test_client()

    def tearDown(self):
        """Clean up the test environment."""
        # This cleanup is simple. For a real app with a DB, this would be more complex.
        pass

    def test_index_route(self):
        """Test the index route to ensure the server is responsive."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CoolSpace AI Backend Service is running', response.data)

    def test_upload_scan_success(self):
        """Test the /api/v1/upload_scan endpoint with valid data."""
        # Mock OBJ data, similar to what the mobile app would send.
        mock_obj_data = b"# Mock OBJ file\nv 1.0 1.0 0.0\nv 1.0 0.0 0.0\nf 1 2 3\n"

        response = self.client.post('/api/v1/upload_scan', data=mock_obj_data)

        # Check for a successful creation status code.
        self.assertEqual(response.status_code, 201)

        # Check the response content.
        json_data = response.get_json()
        self.assertEqual(json_data['message'], 'Scan uploaded successfully.')
        self.assertIn('scan_id', json_data)
        self.assertIn('filename', json_data)
        self.assertEqual(json_data['size_bytes'], len(mock_obj_data))

        # Verify that the file was actually saved.
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], json_data['filename'])
        self.assertTrue(os.path.exists(filepath))

        # Verify the content of the saved file.
        with open(filepath, 'rb') as f:
            saved_data = f.read()
        self.assertEqual(saved_data, mock_obj_data)

    def test_upload_scan_no_data(self):
        """Test the upload endpoint with no data provided."""
        response = self.client.post('/api/v1/upload_scan')

        # Check for a bad request status code.
        self.assertEqual(response.status_code, 400)

        # Check the error message.
        json_data = response.get_json()
        self.assertEqual(json_data['error'], 'No data provided in the request.')

if __name__ == '__main__':
    unittest.main()
