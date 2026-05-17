from tests.api.payloads import valid_employee_payload as _payload


def _seed(api_client, **kwargs):
    api_client.post("/employees", json=_payload(**kwargs))


def test_headcount_empty_returns_three_empty_lists(api_client):
    response = api_client.get("/insights/headcount")

    assert response.status_code == 200
    assert response.json() == {
        "by_country": [],
        "by_department": [],
        "by_job_title": [],
    }


def test_headcount_sorted_by_count_desc_and_excludes_terminated(api_client):
    # Active: IN/Engineering/Engineer x2, US/Engineering/Engineer x1.
    _seed(api_client, employee_id="EMP-A", email="a@x.com",
          country="IN", department="Engineering", job_title="Engineer")
    _seed(api_client, employee_id="EMP-B", email="b@x.com",
          country="IN", department="Engineering", job_title="Engineer")
    _seed(api_client, employee_id="EMP-C", email="c@x.com",
          country="US", department="Engineering", job_title="Engineer")
    # Terminated: must not affect counts.
    _seed(api_client, employee_id="EMP-T", email="t@x.com",
          country="IN", department="Engineering", job_title="Engineer",
          status="terminated")

    response = api_client.get("/insights/headcount")

    body = response.json()
    assert body["by_country"] == [
        {"name": "IN", "count": 2},
        {"name": "US", "count": 1},
    ]
    assert body["by_department"] == [{"name": "Engineering", "count": 3}]
    assert body["by_job_title"] == [{"name": "Engineer", "count": 3}]
