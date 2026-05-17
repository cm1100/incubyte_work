from tests.api.payloads import valid_employee_payload as _payload


def test_get_employees_empty_returns_zero_total_and_empty_items(api_client):
    response = api_client.get("/employees")

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0


def test_get_employees_returns_created_items(api_client):
    api_client.post("/employees", json=_payload())

    response = api_client.get("/employees")

    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["employee_id"] == "EMP-00042"


def test_get_employees_paginates_via_offset_and_limit(api_client):
    for i in range(12):
        api_client.post(
            "/employees",
            json=_payload(employee_id=f"EMP-{i:05d}", email=f"u{i}@x.com"),
        )

    response = api_client.get("/employees?offset=5&limit=3")

    body = response.json()
    assert body["total"] == 12
    assert body["offset"] == 5
    assert body["limit"] == 3
    assert len(body["items"]) == 3


def test_get_employees_filters_by_search(api_client):
    api_client.post(
        "/employees",
        json=_payload(employee_id="EMP-A", email="a@x.com", first_name="Alice"),
    )
    api_client.post(
        "/employees",
        json=_payload(employee_id="EMP-B", email="b@x.com", first_name="Bob"),
    )

    response = api_client.get("/employees?search=alice")

    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["first_name"] == "Alice"
