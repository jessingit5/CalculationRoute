from fastapi.testclient import TestClient
from uuid import uuid4

def test_calculation_bread_flow(client: TestClient):
    unique_username = f"calcuser_{uuid4()}"
    unique_email = f"calc_{uuid4()}@example.com"
    client.post("/users/register", json={"username": unique_username, "email": unique_email, "password": "password123"})
    login_res = client.post("/users/login", data={"username": unique_username, "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    add_res = client.post("/calculations/", json={"a": 10, "b": 5, "type": "add"}, headers=headers)
    assert add_res.status_code == 201
    data = add_res.json()
    assert data["a"] == 10
    assert data["result"] == 15.0
    calc_id = data["id"]

    browse_res = client.get("/calculations/", headers=headers)
    assert browse_res.status_code == 200
    assert len(browse_res.json()) == 1

    read_res = client.get(f"/calculations/{calc_id}", headers=headers)
    assert read_res.status_code == 200
    assert read_res.json()["result"] == 15.0


    edit_res = client.put(f"/calculations/{calc_id}", json={"a": 20, "b": 5, "type": "subtract"}, headers=headers)
    assert edit_res.status_code == 200
    assert edit_res.json()["result"] == 15.0 

    delete_res = client.delete(f"/calculations/{calc_id}", headers=headers)
    assert delete_res.status_code == 204

    verify_res = client.get(f"/calculations/{calc_id}", headers=headers)
    assert verify_res.status_code == 404