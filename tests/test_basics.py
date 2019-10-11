import unittest
from flask import current_app
from app import createApp, db

class BasicsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = createApp('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    # Destruir
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
