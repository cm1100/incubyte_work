from tests.api.payloads import valid_employee_payload as _payload


def test_get_employee_by_id_returns_200_with_body(api_client):
    api_client.post("/employees", json=_payload(employee_id="EMP-77777"))

    response = api_client.get("/employees/EMP-77777")

    assert response.status_code == 200
    body = response.json()
    assert body["employee_id"] == "EMP-77777"
    assert body["full_name"] == "Asha Sharma"


def test_get_employee_by_id_returns_404_when_missing(api_client):
    response = api_client.get("/employees/EMP-NOPE")

    assert response.status_code == 404
