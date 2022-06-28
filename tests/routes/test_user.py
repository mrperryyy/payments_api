
def test_user_test(client):
    response = client.get("/user/test")
    assert response.json["testing"] == "the fdkfjdslkfjsk"