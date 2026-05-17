from tests.api.payloads import valid_employee_payload as _payload


def _seed(api_client, **kwargs):
    api_client.post("/employees", json=_payload(**kwargs))


def test_jobs_in_country_returns_aggregates_per_title(api_client):
    # IN: 2 Engineers (1000, 3000), 1 Manager (5000)
    _seed(api_client, employee_id="EMP-A", email="a@x.com",
          country="IN", currency_code="INR", job_title="Engineer", salary="1000")
    _seed(api_client, employee_id="EMP-B", email="b@x.com",
          country="IN", currency_code="INR", job_title="Engineer", salary="3000")
    _seed(api_client, employee_id="EMP-C", email="c@x.com",
          country="IN", currency_code="INR", job_title="Manager", salary="5000")
    # US Engineer — excluded from IN aggregation
    _seed(api_client, employee_id="EMP-D", email="d@x.com",
          country="US", currency_code="USD", job_title="Engineer", salary="99999")

    response = api_client.get("/insights/by-country/IN/by-job-title")

    assert response.status_code == 200
    data = {r["job_title"]: r for r in response.json()}
    assert data["Engineer"]["count"] == 2
    assert data["Engineer"]["avg_salary"] == "2000.00"
    assert data["Manager"]["count"] == 1
    assert len(data) == 2


def test_jobs_in_unknown_country_returns_empty_200(api_client):
    response = api_client.get("/insights/by-country/XX/by-job-title")

    assert response.status_code == 200
    assert response.json() == []


def test_jobs_with_malformed_country_returns_422(api_client):
    """Path param is validated as 2-char uppercase ISO code."""
    response = api_client.get("/insights/by-country/india/by-job-title")

    assert response.status_code == 422
