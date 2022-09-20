from flaskr import create_app

# method to call the test configuration methods and initialize them if they are not already active 
def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

# method to test the simple hello world example route created at the beginning of the flask lab 
def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'
    