"""Shared request-body builders for API tests."""


def valid_employee_payload(**overrides) -> dict:
    """Minimal-valid POST /employees body. Tests override only what they
    assert on, so future schema changes don't ripple through unrelated
    tests."""
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
