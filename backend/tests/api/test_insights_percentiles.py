from tests.api.payloads import valid_employee_payload as _payload


def _seed(api_client, **kwargs):
    api_client.post("/employees", json=_payload(**kwargs))


def test_percentiles_for_known_distribution(api_client):
    """[100, 200, 300, 400] with statistics.quantiles(method='inclusive'):
    p25=175, p50=250, p75=325, p90=370. Inclusive picked because the
    default 'exclusive' extrapolates beyond [min, max] (e.g. p90 = 450
    even though max = 400), which is nonsense for bounded salary data."""
    for i, sal in enumerate([100, 200, 300, 400]):
        _seed(api_client, employee_id=f"EMP-{i}", email=f"e{i}@x.com",
              country="IN", currency_code="INR", salary=str(sal))

    response = api_client.get("/insights/by-country/IN/percentiles")

    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 1
    row = rows[0]
    assert row["country"] == "IN"
    assert row["currency_code"] == "INR"
    assert row["count"] == 4
    assert row["p25"] == "175.00"
    assert row["p50"] == "250.00"
    assert row["p75"] == "325.00"
    assert row["p90"] == "370.00"


def test_percentiles_with_single_employee_collapses_to_that_salary(api_client):
    _seed(api_client, employee_id="EMP-SOLO", email="s@x.com",
          country="IN", currency_code="INR", salary="50000")

    response = api_client.get("/insights/by-country/IN/percentiles")

    assert response.status_code == 200
    row = response.json()[0]
    assert row["count"] == 1
    assert row["p25"] == row["p50"] == row["p75"] == row["p90"] == "50000.00"


def test_percentiles_for_empty_country_returns_empty_list(api_client):
    response = api_client.get("/insights/by-country/XX/percentiles")

    assert response.status_code == 200
    assert response.json() == []
