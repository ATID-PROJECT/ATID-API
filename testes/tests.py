""" Esta é uma estrutura básica para encontrar todos os testes desenvolvidos e rodá-los. """
import unittest
import sys

sys.path.append("..")
from app import app as meu_web_app

class TestHome(unittest.TestCase):

	def test_get(self):
		"Verifica se a página inicial está funcionando"

		#:  expondo o cliente de teste Werkzeug
		app = meu_web_app.test_client()
		response = app.get('/')
		self.assertEqual(200, response.status_code)


if __name__ == '__main__':
    unittest.main()