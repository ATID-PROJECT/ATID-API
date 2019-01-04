# tests/test_account.py

import unittest 
from app import create_app

class BasicTests(unittest.TestCase):
 
    ############################
    #### setup ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        self.app = create_app()
        self.app = self.app.test_client()

    ###############
    #### tests ####
    ###############
 
    def test_found_pages(self):
        response_login = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response_login.status_code, 200)

        response_signup = self.app.get('/signup', follow_redirects=True)
        self.assertEqual(response_signup.status_code, 200)

        response_logout = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response_logout.status_code, 200)

        response_email_confirm = self.app.get('/email/confirmation/new', follow_redirects=True)
        self.assertEqual(response_email_confirm.status_code, 200)

        response_account_confirm = self.app.get('/confirm-account/<token>', follow_redirects=True)
        self.assertEqual(response_account_confirm.status_code, 200)

    def test_signup_login_logout(self):
        response_signup = register(self.app, "Admin", "Admin", "admin@mail.com", "123")
        self.assertEqual(response_signup.status_code, 200)
        self.assertIn(b'You are now logged in', response_signup.data)

        response_login = login(self.app, "admin@mail.com", "123")
        self.assertEqual(response_login.status_code, 200)
        self.assertIn(b'Welcome', response_login.data)

        response_logout = logout(self.app)
        self.assertEqual(response_logout.status_code, 200)
    
    ########################
    #### helper methods ####
    ########################
 
def register(client, first_name, last_name, email, password):
    return client.post(
        '/signup', data=dict(
            first_name=first_name,
            last_name=last_name, 
            email=email,
            password=password,
        ),  follow_redirects=True)
 
def login(client, email, password):
    return client.post(
        '/login',
        data=dict(email=email, password=password),
        follow_redirects=True
    )
 
def logout(client):
    return client.get(
        '/logout',
        follow_redirects=True
    )

if __name__ == "__main__":
    unittest.main()