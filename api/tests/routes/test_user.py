from unittest.mock import patch

@patch('api.routes.user.check_username_unique')
@patch('api.routes.user.add_user')
@patch('api.routes.user.url_for', return_value=None)
def test_create_user(check_user, add_user, url_for, client):
    user_data = {'username': 'user1', 'password': 'password'}
    response = client.post("/user", json=user_data)
    assert response.status_code == 201
    assert response.json['username'] == 'user1'

@patch('api.routes.helpers.find_user', return_value='user1')
def test_username_taken(find_user, client):
    user_data = {'username': 'user1', 'password': 'password'}
    response = client.post("/user", json=user_data)
    assert response.status_code == 400
