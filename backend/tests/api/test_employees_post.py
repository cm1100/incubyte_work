def _valid_payload(**overrides):
    """Minimal-valid POST body. Tests override only the field they assert on."""
    body = {
        "employee_id": "EMP-00042",
        "first_name": "Asha",
        "last_name": "Sharma",
        "email": "asha@example.com",
        "job_title": "Senior Engineer",
        "department": "Engineering",
        "country": "IN",
        "salary": "1500000.00",
        "currency_code": "INR",
        "hire_date": "2023-01-15",
    }
    body.update(overrides)
    return body


def test_post_employee_returns_201_with_created_resource(api_client):
    response = api_client.post("/employees", json=_valid_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["employee_id"] == "EMP-00042"
    assert body["full_name"] == "Asha Sharma"
    assert body["status"] == "active"
    assert body["employment_type"] == "full_time"
    assert body["created_at"] is not None


def test_post_duplicate_email_returns_409(api_client):
    """Email is a uniqueness contract. The repo raises IntegrityError;
    the API must surface that as 409 Conflict — never 500."""
    api_client.post(
        "/employees",
        json=_valid_payload(employee_id="EMP-A", email="dup@example.com"),
    )

    response = api_client.post(
        "/employees",
        json=_valid_payload(employee_id="EMP-B", email="dup@example.com"),
    )

    assert response.status_code == 409


def test_post_with_invalid_email_returns_422(api_client):
    """Pydantic validates EmailStr; the route never sees the request.
    Documents the contract so a regression (e.g. switching to plain str)
    is caught."""
    response = api_client.post("/employees", json=_valid_payload(email="not-an-email"))

    assert response.status_code == 422


def test_post_with_negative_salary_returns_422(api_client):
    """Field(ge=0) catches this at the schema layer — DB constraint is
    defence in depth, not the primary."""
    response = api_client.post("/employees", json=_valid_payload(salary="-1.00"))

    assert response.status_code == 422
