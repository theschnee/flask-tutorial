import pytest
from flaskr.db import get_db

# method to test the indexing method, which should give all the information about a specific blog post that is necessary 
def test_index(client, auth):
    
    # getting the login or registration pages  
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    # logging in
    auth.login()

    # checking data fields and different pages in charge of blog post manipulation 
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data

# method to create patameters for different page paths related to the blog page (for test_login_required)
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))

# testing the check for required login before blog posting 
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"

# check that the function checking for a blog post author functions as intended 
def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data

# method to create patameters for different page paths related to the blog page (for test_exists_required)
@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))

# method to check on whether the path to a post exists or not 
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

# method to test creation of a blog post 
def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2

# method to test updating of a blog post 
def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'

# method to create patameters for different page paths related to the blog page (for test_create_update_validate)
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))

# method to test for validation of the update to the blog post based on fields entered 
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data

# method to test deletion of a blog post 
def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None
        