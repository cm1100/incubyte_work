from tests.api.payloads import valid_employee_payload as _payload


def _seed(api_client, country, currency, salaries, status="active", id_prefix="A"):
    for i, sal in enumerate(salaries):
        api_client.post(
            "/employees",
            json=_payload(
                employee_id=f"EMP-{id_prefix}-{i}",
                email=f"{id_prefix.lower()}{i}@x.com",
                country=country,
                currency_code=currency,
                salary=str(sal),
                status=status,
            ),
        )


def test_by_country_returns_empty_list_when_no_employees(api_client):
    response = api_client.get("/insights/by-country")

    assert response.status_code == 200
    assert response.json() == []


def test_by_country_returns_min_max_avg_excluding_terminated(api_client):
    _seed(api_client, "IN", "INR", [1000, 2000, 3000], id_prefix="IN")
    _seed(api_client, "US", "USD", [50000, 70000], id_prefix="US")
    _seed(api_client, "IN", "INR", [9999], status="terminated", id_prefix="INT")

    response = api_client.get("/insights/by-country")
    assert response.status_code == 200
    data = {(r["country"], r["currency_code"]): r for r in response.json()}

    assert data[("IN", "INR")]["count"] == 3
    assert data[("IN", "INR")]["min_salary"] == "1000.00"
    assert data[("IN", "INR")]["max_salary"] == "3000.00"
    assert data[("IN", "INR")]["avg_salary"] == "2000.00"

    assert data[("US", "USD")]["count"] == 2
    assert data[("US", "USD")]["avg_salary"] == "60000.00"
