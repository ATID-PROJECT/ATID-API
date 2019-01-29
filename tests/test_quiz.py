# test_quiz.py
import unittest
import os
import json
from app import create_app

class QuizTestCase(unittest.TestCase):
    """This class represents the quiz test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.quiz_base = {
            "name": "1998-10-10",
            "description": "1998-10-10",
            "time_limit": "1",
            "time_type": "1",
            "open_date": "1",
            "end_date": "",
            "new_page": "",
            "shuffle": "",
            "id_network": ""
        }


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
