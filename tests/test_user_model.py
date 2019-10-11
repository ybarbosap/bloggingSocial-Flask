import unittest
from app.models import User

class UserModelTestCase(unittest.TestCase):

    # teste para criação de um hash de senha
    def testPasswordSetter(self):
        u = User(password = 'cat')
        self.assertTrue(u.password_hash is not None)

    # teste de leitura     
    def testNoPasswordGetter(self):
        u = User(password = 'cat')
        with self.assertRaises(AttributeError):
            u.password  

    # teste de verificação
    def testPasswordVerification(self):
        u = User(password = 'cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    # teste de comparação com hash's criados a partir da mesma senha
    def testPasswordSalts_areRandom(self):
        u = User(password = 'cat')
        u2 = User(password = 'cat')
        self.assertTrue(u.password_hash != u2.password_hash)