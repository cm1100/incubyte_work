from tests.api.payloads import valid_employee_payload as _payload


# ---------- PATCH ----------


def test_patch_employee_returns_200_with_updated_body(api_client):
    api_client.post("/employees", json=_payload(employee_id="EMP-100"))

    response = api_client.patch(
        "/employees/EMP-100", json={"job_title": "Staff Engineer"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["job_title"] == "Staff Engineer"
    assert body["employee_id"] == "EMP-100"  # untouched


def test_patch_partial_update_leaves_other_fields_alone(api_client):
    api_client.post(
        "/employees",
        json=_payload(employee_id="EMP-200", department="Engineering"),
    )

    api_client.patch("/employees/EMP-200", json={"salary": "2000000.00"})

    body = api_client.get("/employees/EMP-200").json()
    assert body["department"] == "Engineering"
    assert body["salary"] == "2000000.00"


def test_patch_returns_404_when_employee_missing(api_client):
    response = api_client.patch("/employees/EMP-GHOST", json={"job_title": "X"})

    assert response.status_code == 404


def test_patch_to_duplicate_email_returns_409(api_client):
    api_client.post("/employees", json=_payload(employee_id="EMP-A", email="a@x.com"))
    api_client.post("/employees", json=_payload(employee_id="EMP-B", email="b@x.com"))

    response = api_client.patch("/employees/EMP-B", json={"email": "a@x.com"})

    assert response.status_code == 409


def test_patch_with_invalid_email_returns_422(api_client):
    api_client.post("/employees", json=_payload(employee_id="EMP-300"))

    response = api_client.patch("/employees/EMP-300", json={"email": "not-an-email"})

    assert response.status_code == 422


# ---------- DELETE ----------


def test_delete_employee_returns_204(api_client):
    api_client.post("/employees", json=_payload(employee_id="EMP-DEL"))

    response = api_client.delete("/employees/EMP-DEL")

    assert response.status_code == 204
    # Subsequent GET confirms it's actually gone.
    assert api_client.get("/employees/EMP-DEL").status_code == 404


def test_delete_returns_404_when_employee_missing(api_client):
    response = api_client.delete("/employees/EMP-GHOST")

    assert response.status_code == 404
