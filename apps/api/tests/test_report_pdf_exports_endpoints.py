from unittest.mock import patch

import pytest

from app.services.daily_operational_summary import (
    get_daily_operational_summary,
)
from app.services.management_dashboard import get_management_dashboard
from app.services.monthly_operational_summary import (
    get_monthly_operational_summary,
)
from app.services.pdf_export import (
    PDF_MEDIA_TYPE,
    add_empty_message,
    add_key_value_table,
)
from tests.test_management_dashboard_endpoints import _seed_management_data
from tests.test_report_exports_endpoints import _business_record_counts

PDF_EXPORT_URLS = [
    "/api/v1/reports/exports/management-dashboard.pdf",
    "/api/v1/reports/exports/monthly-summary.pdf?year=2026&month=7",
    "/api/v1/reports/exports/daily-operational-summary.pdf?date=2026-07-10",
    "/api/v1/reports/exports/receivables.pdf",
    "/api/v1/reports/exports/payroll.pdf",
]

DATED_PDF_EXPORT_URLS = [
    "/api/v1/reports/exports/management-dashboard.pdf",
    "/api/v1/reports/exports/receivables.pdf",
    "/api/v1/reports/exports/payroll.pdf",
]


@pytest.mark.parametrize("url", PDF_EXPORT_URLS)
def test_report_pdf_export_requires_authentication(api_client, url: str) -> None:
    client, _ = api_client

    response = client.get(url)

    assert response.status_code == 401


@pytest.mark.parametrize("url", PDF_EXPORT_URLS)
def test_report_pdf_export_returns_valid_pdf_without_data(
    api_client,
    api_auth_headers,
    url: str,
) -> None:
    client, _ = api_client

    response = client.get(url, headers=api_auth_headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == PDF_MEDIA_TYPE
    assert ".pdf" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF-")
    assert response.content.rstrip().endswith(b"%%EOF")
    assert len(response.content) > 1_000


@pytest.mark.parametrize("url", DATED_PDF_EXPORT_URLS)
def test_report_pdf_export_rejects_inverted_date_range(
    api_client,
    api_auth_headers,
    url: str,
) -> None:
    client, _ = api_client

    response = client.get(
        f"{url}?date_from=2026-07-31&date_to=2026-07-01",
        headers=api_auth_headers,
    )

    assert response.status_code == 400


def test_monthly_pdf_requires_valid_year_and_month(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    missing_period = client.get(
        "/api/v1/reports/exports/monthly-summary.pdf",
        headers=api_auth_headers,
    )
    invalid_month = client.get(
        "/api/v1/reports/exports/monthly-summary.pdf?year=2026&month=13",
        headers=api_auth_headers,
    )

    assert missing_period.status_code == 422
    assert invalid_month.status_code == 422


def test_daily_pdf_requires_date(api_client, api_auth_headers) -> None:
    client, _ = api_client

    response = client.get(
        "/api/v1/reports/exports/daily-operational-summary.pdf",
        headers=api_auth_headers,
    )

    assert response.status_code == 422


def test_pdf_exports_reuse_official_report_services(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    with patch(
        "app.services.pdf_export.get_management_dashboard",
        wraps=get_management_dashboard,
    ) as management_builder:
        response = client.get(
            PDF_EXPORT_URLS[0],
            headers=api_auth_headers,
        )
        assert response.status_code == 200
        management_builder.assert_called_once()

    with patch(
        "app.services.pdf_export.get_monthly_operational_summary",
        wraps=get_monthly_operational_summary,
    ) as monthly_builder:
        response = client.get(
            PDF_EXPORT_URLS[1],
            headers=api_auth_headers,
        )
        assert response.status_code == 200
        monthly_builder.assert_called_once()

    with patch(
        "app.services.pdf_export.get_daily_operational_summary",
        wraps=get_daily_operational_summary,
    ) as daily_builder:
        response = client.get(
            PDF_EXPORT_URLS[2],
            headers=api_auth_headers,
        )
        assert response.status_code == 200
        daily_builder.assert_called_once()


def test_all_pdf_exports_are_read_only(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    before = _business_record_counts(testing_session_local)

    for url in PDF_EXPORT_URLS:
        response = client.get(url, headers=api_auth_headers)
        assert response.status_code == 200

    assert _business_record_counts(testing_session_local) == before


def test_pdf_exports_render_registered_business_data(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    _seed_management_data(testing_session_local)

    urls = [
        (
            "/api/v1/reports/exports/management-dashboard.pdf"
            "?date_from=2026-07-01&date_to=2026-07-31"
        ),
        "/api/v1/reports/exports/monthly-summary.pdf?year=2026&month=7",
        "/api/v1/reports/exports/daily-operational-summary.pdf?date=2026-07-10",
        (
            "/api/v1/reports/exports/receivables.pdf"
            "?date_from=2026-07-01&date_to=2026-07-31"
        ),
        (
            "/api/v1/reports/exports/payroll.pdf"
            "?date_from=2026-07-01&date_to=2026-07-31"
        ),
    ]

    for url in urls:
        response = client.get(url, headers=api_auth_headers)
        assert response.status_code == 200
        assert response.content.startswith(b"%PDF-")


def test_receivables_pdf_excludes_voided_activity_from_main_totals(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    _seed_management_data(testing_session_local)

    with patch(
        "app.services.pdf_export.add_key_value_table",
        wraps=add_key_value_table,
    ) as summary_table:
        response = client.get(
            (
                "/api/v1/reports/exports/receivables.pdf"
                "?date_from=2026-07-01&date_to=2026-07-31"
            ),
            headers=api_auth_headers,
        )

    assert response.status_code == 200
    values = dict(summary_table.call_args_list[0].args[1])
    assert values["Total vendido a crédito"] == "$60.00"
    assert values["Total cobrado"] == "$20.00"
    assert values["Saldo pendiente"] == "$40.00"


def test_payroll_pdf_excludes_voided_runs_from_main_totals(
    api_client,
    api_auth_headers,
) -> None:
    client, testing_session_local = api_client
    _seed_management_data(testing_session_local)

    with patch(
        "app.services.pdf_export.add_key_value_table",
        wraps=add_key_value_table,
    ) as summary_table:
        response = client.get(
            (
                "/api/v1/reports/exports/payroll.pdf"
                "?date_from=2026-07-01&date_to=2026-07-31"
            ),
            headers=api_auth_headers,
        )

    assert response.status_code == 200
    values = dict(summary_table.call_args_list[0].args[1])
    assert values["Total bruto"] == "$1,000.00"
    assert values["Neto total"] == "$900.00"
    assert values["Roles activos"] == 1
    assert values["Roles anulados"] == 1


def test_empty_period_pdf_contains_no_data_message(
    api_client,
    api_auth_headers,
) -> None:
    client, _ = api_client

    with patch(
        "app.services.pdf_export.add_empty_message",
        wraps=add_empty_message,
    ) as empty_message:
        response = client.get(
            "/api/v1/reports/exports/monthly-summary.pdf?year=2026&month=7",
            headers=api_auth_headers,
        )

    assert response.status_code == 200
    assert any(
        call.args[1] == "Sin datos para el período"
        for call in empty_message.call_args_list
    )
