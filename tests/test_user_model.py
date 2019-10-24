import unittest
from app.models import (
    User, AnonymousUser, Role, Permission
)

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

    def test_user_role(self):
        u = User(email='john@example.com', password='dog')
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))