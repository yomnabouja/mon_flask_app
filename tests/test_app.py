import unittest
from app import create_app  # importe la factory Flask

class BasicTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Adapte le texte selon ton index.html
        self.assertIn(b'Bienvenue', response.data)

if __name__ == "__main__":
    unittest.main()