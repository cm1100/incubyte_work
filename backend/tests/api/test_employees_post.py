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
