from collections.abc import Iterable, Sequence
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from html import escape
from io import BytesIO
import re
from typing import Any

from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    CondPageBreak,
    Flowable,
    LongTable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session

from app.services import payroll as payroll_service
from app.services import receivables as receivable_service
from app.services.daily_operational_summary import (
    get_daily_operational_summary,
)
from app.services.management_dashboard import get_management_dashboard
from app.services.monthly_operational_summary import (
    get_monthly_operational_summary,
)

PDF_MEDIA_TYPE = "application/pdf"
PDF_PAGE_SIZE = landscape(A4)
PAGE_MARGIN = 12 * mm
CONTENT_WIDTH = PDF_PAGE_SIZE[0] - (PAGE_MARGIN * 2)
MONEY_QUANTUM = Decimal("0.01")
QUANTITY_QUANTUM = Decimal("0.001")
CONTROL_CHARACTERS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

TEAL = colors.HexColor("#0F766E")
TEAL_DARK = colors.HexColor("#115E59")
TEAL_LIGHT = colors.HexColor("#CCFBF1")
SLATE = colors.HexColor("#334155")
SLATE_LIGHT = colors.HexColor("#E2E8F0")
ROW_ALT = colors.HexColor("#F8FAFC")
WARNING = colors.HexColor("#B45309")

_BASE_STYLES = getSampleStyleSheet()
TITLE_STYLE = ParagraphStyle(
    "PdfTitle",
    parent=_BASE_STYLES["Title"],
    fontName="Helvetica-Bold",
    fontSize=19,
    leading=23,
    alignment=TA_LEFT,
    textColor=TEAL_DARK,
    spaceAfter=5 * mm,
)
META_STYLE = ParagraphStyle(
    "PdfMeta",
    parent=_BASE_STYLES["BodyText"],
    fontName="Helvetica",
    fontSize=8,
    leading=11,
    textColor=SLATE,
    spaceAfter=1 * mm,
)
SECTION_STYLE = ParagraphStyle(
    "PdfSection",
    parent=_BASE_STYLES["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
    textColor=TEAL_DARK,
    spaceBefore=4 * mm,
    spaceAfter=2 * mm,
)
BODY_STYLE = ParagraphStyle(
    "PdfBody",
    parent=_BASE_STYLES["BodyText"],
    fontName="Helvetica",
    fontSize=8,
    leading=10,
    textColor=SLATE,
)
TABLE_HEADER_STYLE = ParagraphStyle(
    "PdfTableHeader",
    parent=BODY_STYLE,
    fontName="Helvetica-Bold",
    fontSize=7,
    leading=9,
    alignment=TA_CENTER,
    textColor=colors.white,
)
TABLE_CELL_STYLE = ParagraphStyle(
    "PdfTableCell",
    parent=BODY_STYLE,
    fontSize=7,
    leading=9,
)
TABLE_CELL_CENTER_STYLE = ParagraphStyle(
    "PdfTableCellCenter",
    parent=TABLE_CELL_STYLE,
    alignment=TA_CENTER,
)
EMPTY_STYLE = ParagraphStyle(
    "PdfEmpty",
    parent=BODY_STYLE,
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=12,
    textColor=WARNING,
    backColor=colors.HexColor("#FFFBEB"),
    borderColor=colors.HexColor("#FDE68A"),
    borderWidth=1,
    borderPadding=7,
    spaceBefore=2 * mm,
    spaceAfter=3 * mm,
)


def build_pdf_response(buffer: BytesIO, filename: str) -> StreamingResponse:
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type=PDF_MEDIA_TYPE,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{_safe_filename(filename)}"'
            ),
            "Cache-Control": "no-store",
        },
    )


def create_pdf_document(
    title: str,
    period: str,
) -> tuple[SimpleDocTemplate, BytesIO, list[Flowable]]:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=PDF_PAGE_SIZE,
        leftMargin=PAGE_MARGIN,
        rightMargin=PAGE_MARGIN,
        topMargin=12 * mm,
        bottomMargin=15 * mm,
        title=safe_text(title),
        author="Agua Activa ERP",
        subject="Reporte ejecutivo de solo lectura",
        pageCompression=1,
    )
    story: list[Flowable] = []
    add_title(story, title, period)
    return document, buffer, story


def add_title(story: list[Flowable], title: str, period: str) -> None:
    story.append(Paragraph(safe_text(title), TITLE_STYLE))
    story.append(
        Paragraph(f"<b>Período:</b> {safe_text(period)}", META_STYLE)
    )
    story.append(
        Paragraph(
            (
                "<b>Generado:</b> "
                f"{safe_text(format_date(datetime.now().astimezone()))}"
            ),
            META_STYLE,
        )
    )
    story.append(Spacer(1, 2 * mm))


def add_section_heading(story: list[Flowable], heading: str) -> None:
    story.append(CondPageBreak(20 * mm))
    story.append(Paragraph(safe_text(heading), SECTION_STYLE))


def add_key_value_table(
    story: list[Flowable],
    values: Sequence[tuple[str, Any]],
    *,
    columns: int = 2,
) -> None:
    if not values:
        add_empty_message(story)
        return

    rows: list[list[Flowable | str]] = []
    row: list[Flowable | str] = []
    for label, value in values:
        row.extend(
            [
                _paragraph(label, TABLE_CELL_STYLE, max_length=70),
                _paragraph(value, TABLE_CELL_STYLE, max_length=110),
            ]
        )
        if len(row) == columns * 2:
            rows.append(row)
            row = []
    if row:
        row.extend([""] * ((columns * 2) - len(row)))
        rows.append(row)

    if columns == 1:
        widths = [CONTENT_WIDTH * 0.32, CONTENT_WIDTH * 0.68]
    else:
        widths = [
            CONTENT_WIDTH * 0.18,
            CONTENT_WIDTH * 0.32,
        ] * columns
    table = Table(rows, colWidths=widths, hAlign="LEFT")
    commands: list[tuple[Any, ...]] = [
        ("GRID", (0, 0), (-1, -1), 0.35, SLATE_LIGHT),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for label_column in range(0, columns * 2, 2):
        commands.extend(
            [
                ("BACKGROUND", (label_column, 0), (label_column, -1), TEAL_LIGHT),
                (
                    "FONTNAME",
                    (label_column, 0),
                    (label_column, -1),
                    "Helvetica-Bold",
                ),
            ]
        )
    table.setStyle(TableStyle(commands))
    story.append(table)
    story.append(Spacer(1, 2 * mm))


def add_data_table(
    story: list[Flowable],
    headers: Sequence[str],
    rows: Iterable[Sequence[Any]],
    *,
    column_widths: Sequence[Any] | None = None,
    centered_columns: Sequence[int] = (),
) -> None:
    normalized_rows = list(rows)
    if not normalized_rows:
        add_empty_message(story)
        return

    header_cells = [
        _paragraph(header, TABLE_HEADER_STYLE, max_length=80)
        for header in headers
    ]
    body_rows: list[list[Paragraph]] = []
    for source_row in normalized_rows:
        row: list[Paragraph] = []
        for index in range(len(headers)):
            value = source_row[index] if index < len(source_row) else ""
            style = (
                TABLE_CELL_CENTER_STYLE
                if index in centered_columns
                else TABLE_CELL_STYLE
            )
            row.append(_paragraph(value, style, max_length=100))
        body_rows.append(row)

    widths = (
        list(column_widths)
        if column_widths is not None
        else [CONTENT_WIDTH / len(headers)] * len(headers)
    )
    table = LongTable(
        [header_cells, *body_rows],
        colWidths=widths,
        repeatRows=1,
        splitByRow=1,
        hAlign="LEFT",
    )
    commands: list[tuple[Any, ...]] = [
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("GRID", (0, 0), (-1, -1), 0.35, SLATE_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for row_index in range(2, len(body_rows) + 1, 2):
        commands.append(("BACKGROUND", (0, row_index), (-1, row_index), ROW_ALT))
    table.setStyle(TableStyle(commands))
    story.append(table)
    story.append(Spacer(1, 2 * mm))


def add_empty_message(
    story: list[Flowable],
    message: str = "Sin datos",
) -> None:
    story.append(Paragraph(safe_text(message), EMPTY_STYLE))


def format_money(value: Decimal | None) -> str:
    normalized = (value or Decimal("0.00")).quantize(
        MONEY_QUANTUM,
        rounding=ROUND_HALF_UP,
    )
    return f"${normalized:,.2f}"


def format_quantity(value: Decimal | None) -> str:
    normalized = (value or Decimal("0.000")).quantize(
        QUANTITY_QUANTUM,
        rounding=ROUND_HALF_UP,
    )
    return f"{normalized:,.3f}"


def format_date(value: date | datetime | None) -> str:
    if value is None:
        return "-"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return value.isoformat()


def safe_text(value: Any, *, max_length: int | None = None) -> str:
    if value is None:
        return "-"
    text = CONTROL_CHARACTERS_RE.sub("", str(value))
    text = text.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    text = " ".join(text.split())
    if max_length is not None and len(text) > max_length:
        text = f"{text[: max_length - 3].rstrip()}..."
    return escape(text)


def split_long_text(value: Any, max_length: int = 100) -> str:
    return safe_text(value, max_length=max_length)


def build_management_dashboard_pdf(
    db: Session,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
) -> BytesIO:
    report = get_management_dashboard(
        db,
        date_from=date_from,
        date_to=date_to,
    )
    period = (
        f"{format_date(report.period.date_from)} a "
        f"{format_date(report.period.date_to)}"
    )
    document, buffer, story = create_pdf_document(
        "Panel gerencial Agua Activa",
        period,
    )
    if not _management_has_data(report):
        add_empty_message(story, "Sin datos para el período")

    add_section_heading(story, "Indicadores principales")
    add_key_value_table(
        story,
        (
            ("Total ventas", format_money(report.sales.sales_total)),
            ("Cobros", format_money(report.receivables.payments_total)),
            (
                "Cartera pendiente",
                format_money(report.receivables.pending_balance_total),
            ),
            ("Caja final", format_money(report.cash.cash_final_total)),
            (
                "Gastos operativos",
                format_money(
                    report.operating_expenses.operating_expenses_total
                ),
            ),
            ("Compras", format_money(report.purchases.purchases_total)),
            (
                "Producción",
                format_quantity(
                    report.production.production_items_total_quantity
                ),
            ),
            (
                "Nómina neta calculada",
                format_money(report.payroll.net_pay_total),
            ),
        ),
    )

    add_section_heading(story, "Alertas principales")
    add_data_table(
        story,
        ("Tipo", "Alerta", "Detalle", "Cantidad"),
        (
            (
                _status_label(alert.type),
                alert.title,
                alert.message,
                alert.count,
            )
            for alert in report.alerts
        ),
        column_widths=(70, 150, 420, 65),
        centered_columns=(0, 3),
    )

    add_section_heading(story, "Resumen por módulos")
    add_data_table(
        story,
        ("Módulo", "Indicador", "Valor"),
        _management_module_rows(report),
        column_widths=(120, 360, 170),
    )
    return _finish_pdf(document, buffer, story)


def build_monthly_summary_pdf(
    db: Session,
    *,
    year: int,
    month: int,
) -> BytesIO:
    report = get_monthly_operational_summary(db, year=year, month=month)
    period = (
        f"{report.period.year:04d}-{report.period.month:02d} "
        f"({format_date(report.period.date_from)} a "
        f"{format_date(report.period.date_to)})"
    )
    document, buffer, story = create_pdf_document(
        "Resumen mensual Agua Activa",
        period,
    )
    has_data = _monthly_has_data(report)
    if not has_data:
        add_empty_message(story, "Sin datos para el período")

    add_section_heading(story, "Totales principales")
    add_key_value_table(
        story,
        (
            (
                "Ingreso de efectivo de referencia",
                format_money(
                    report.totals.total_business_cash_inflow_reference
                ),
            ),
            ("Caja final", format_money(report.cash_summary.total_final)),
            (
                "Ventas totales",
                format_money(report.sales_summary.total_sales_amount),
            ),
            (
                "Cobros",
                format_money(report.receivables_summary.payments_total),
            ),
            (
                "Cartera pendiente",
                format_money(
                    report.receivables_summary.pending_credit_total
                ),
            ),
            (
                "Producción neta",
                format_quantity(report.production_summary.total_quantity_net),
            ),
            (
                "Efectivo entregado en rutas",
                format_money(
                    report.route_financial_summary.delivered_cash_total
                ),
            ),
            (
                "Recibido de rutas",
                format_money(
                    report.route_cash_receipts_summary.received_amount_total
                ),
            ),
        ),
    )

    for heading, values in _monthly_sections(report):
        add_section_heading(story, heading)
        add_key_value_table(story, values)

    add_section_heading(story, "Alertas")
    add_data_table(
        story,
        ("Código", "Mensaje", "Cantidad"),
        (
            (alert.code, alert.message, alert.count)
            for alert in report.alerts_summary.alerts_by_code
        ),
        column_widths=(180, 440, 75),
        centered_columns=(2,),
    )

    if has_data:
        add_section_heading(story, "Resumen de días del mes")
        add_data_table(
            story,
            (
                "Fecha",
                "Caja final",
                "Producción",
                "Venta contado",
                "Venta crédito",
                "Cobros",
                "Ruta entregada",
                "Ruta recibida",
                "Alertas",
            ),
            (
                (
                    format_date(row.date),
                    format_money(row.cash_total_final),
                    format_quantity(row.production_quantity_net),
                    format_money(row.cash_sales_total),
                    format_money(row.credit_sales_total),
                    format_money(row.payments_total),
                    format_money(row.route_delivered_cash_total),
                    format_money(row.route_cash_registered_total),
                    row.alerts_count,
                )
                for row in report.daily_rows
            ),
            column_widths=(60, 75, 75, 80, 80, 70, 90, 85, 55),
            centered_columns=(0, 8),
        )
    return _finish_pdf(document, buffer, story)


def build_daily_operational_summary_pdf(
    db: Session,
    *,
    report_date: date,
) -> BytesIO:
    report = get_daily_operational_summary(
        db=db,
        report_date=report_date,
    )
    document, buffer, story = create_pdf_document(
        "Resumen operativo diario Agua Activa",
        format_date(report.date),
    )
    if not _daily_has_data(report):
        add_empty_message(story, "Sin datos")

    sections = (
        (
            "Caja del día",
            (
                ("Existe cuadre", _yes_no(report.cash_summary.cash_session_exists)),
                ("Estado", _status_label(report.cash_summary.cash_session_status)),
                ("Total contado", format_money(report.cash_summary.total_counted)),
                ("Gastos de caja", format_money(report.cash_summary.total_expenses)),
                ("Caja final", format_money(report.cash_summary.total_final)),
                (
                    "Recibos de ruta en caja",
                    format_money(report.cash_summary.route_cash_receipts_total),
                ),
            ),
        ),
        (
            "Producción del día",
            (
                (
                    "Producciones activas",
                    report.production_summary.active_production_batches_count,
                ),
                (
                    "Producciones anuladas",
                    report.production_summary.voided_production_batches_count,
                ),
                (
                    "Cantidad producida",
                    format_quantity(
                        report.production_summary.total_quantity_produced
                    ),
                ),
                (
                    "Merma",
                    format_quantity(
                        report.production_summary.total_quantity_waste
                    ),
                ),
                (
                    "Producción neta",
                    format_quantity(report.production_summary.total_quantity_net),
                ),
            ),
        ),
        (
            "Ventas y cobros del día",
            (
                (
                    "Ventas de contado",
                    format_money(report.sales_summary.cash_sales_total),
                ),
                (
                    "Ventas a crédito",
                    format_money(report.sales_summary.credit_sales_total),
                ),
                (
                    "Ventas totales",
                    format_money(report.sales_summary.total_sales_amount),
                ),
                (
                    "Cobros",
                    format_money(report.receivables_summary.payments_total),
                ),
                (
                    "Ventas anuladas",
                    report.sales_summary.voided_sales_count,
                ),
                (
                    "Cobros anulados",
                    report.receivables_summary.voided_payments_count,
                ),
            ),
        ),
        (
            "Gastos del día",
            (
                (
                    "Gastos antes del conteo",
                    format_money(
                        report.cash_summary.pre_count_expenses_total
                    ),
                ),
                (
                    "Gastos después del conteo",
                    format_money(
                        report.cash_summary.post_count_expenses_total
                    ),
                ),
                ("Gastos registrados", report.cash_summary.expenses_count),
                (
                    "Total gastos de caja",
                    format_money(report.cash_summary.total_expenses),
                ),
            ),
        ),
        (
            "Rutas, cierres y recibos",
            (
                (
                    "Cargas activas",
                    report.route_loads_summary.active_route_loads_count,
                ),
                (
                    "Retornos activos",
                    report.route_returns_summary.active_route_returns_count,
                ),
                (
                    "Cierres activos",
                    report.route_closures_summary.active_route_closures_count,
                ),
                (
                    "Efectivo esperado",
                    format_money(
                        report.route_closures_summary.expected_cash_total
                    ),
                ),
                (
                    "Efectivo entregado",
                    format_money(
                        report.route_closures_summary.delivered_cash_total
                    ),
                ),
                (
                    "Recibos activos",
                    report.route_cash_receipts_summary.active_receipts_count,
                ),
                (
                    "Efectivo recibido",
                    format_money(
                        report.route_cash_receipts_summary.received_amount_total
                    ),
                ),
                (
                    "Diferencia de recibos",
                    format_money(
                        report.route_cash_receipts_summary.difference_total
                    ),
                ),
            ),
        ),
    )
    for heading, values in sections:
        add_section_heading(story, heading)
        add_key_value_table(story, values)

    add_section_heading(story, "Alertas del día")
    add_data_table(
        story,
        ("Tipo", "Código", "Mensaje"),
        (
            (_status_label(alert.type), alert.code, alert.message)
            for alert in report.alerts
        ),
        column_widths=(80, 180, 440),
        centered_columns=(0,),
    )
    return _finish_pdf(document, buffer, story)


def build_receivables_pdf(
    db: Session,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    customer_id: int | None = None,
) -> BytesIO:
    _validate_date_range(date_from, date_to)
    customers = receivable_service.list_receivable_customers(
        db=db,
        only_with_balance=True,
        date_from=date_from,
        date_to=date_to,
    )
    if customer_id is not None:
        customers = [
            customer
            for customer in customers
            if customer.customer_id == customer_id
        ]
        statement = receivable_service.get_customer_statement(
            db=db,
            customer_id=customer_id,
            date_from=date_from,
            date_to=date_to,
            include_paid=True,
        )
        summary_values = (
            int(statement.total_balance > Decimal("0.00")),
            statement.total_credit_sales,
            statement.total_paid,
            statement.total_balance,
        )
    else:
        statement = None
        summary = receivable_service.get_receivables_summary(
            db,
            date_from=date_from,
            date_to=date_to,
        )
        summary_values = (
            summary.total_customers_with_balance,
            summary.total_credit_sales,
            summary.total_paid,
            summary.total_balance,
        )

    overdue = [
        item
        for item in receivable_service.list_overdue_receivables(db)
        if (customer_id is None or item.customer_id == customer_id)
        and (date_from is None or item.sale_date >= date_from)
        and (date_to is None or item.sale_date <= date_to)
    ]
    document, buffer, story = create_pdf_document(
        "Cartera y cuentas por cobrar",
        _optional_period(date_from, date_to),
    )
    if not customers and (
        statement is None
        or (
            not statement.credit_sales
            and not statement.payments
            and statement.total_balance == Decimal("0.00")
        )
    ):
        add_empty_message(story, "Sin datos")

    add_section_heading(story, "Resumen de cartera")
    add_key_value_table(
        story,
        (
            ("Total vendido a crédito", format_money(summary_values[1])),
            ("Total cobrado", format_money(summary_values[2])),
            ("Saldo pendiente", format_money(summary_values[3])),
            ("Clientes con saldo", summary_values[0]),
            (
                "Clientes vencidos",
                len({item.customer_id for item in overdue}),
            ),
            (
                "Saldo vencido",
                format_money(
                    sum(
                        (item.balance_amount for item in overdue),
                        start=Decimal("0.00"),
                    )
                ),
            ),
        ),
    )

    add_section_heading(story, "Clientes con saldo")
    add_data_table(
        story,
        ("Cliente", "Total crédito", "Pagado", "Saldo"),
        (
            (
                customer.customer_name,
                format_money(customer.total_credit_sales),
                format_money(customer.total_paid),
                format_money(customer.total_balance),
            )
            for customer in customers
        ),
        column_widths=(310, 130, 130, 130),
    )

    if statement is not None:
        add_section_heading(
            story,
            f"Estado de cuenta resumido - {statement.customer_name}",
        )
        statement_rows = [
            (
                "Venta",
                format_date(sale.sale_date),
                sale.sale_number,
                format_money(sale.total_amount),
                format_money(sale.balance_amount),
                _status_label(sale.credit_status),
            )
            for sale in statement.credit_sales
        ]
        statement_rows.extend(
            (
                "Abono",
                format_date(payment.payment_date),
                payment.sale_number,
                format_money(payment.amount),
                "-",
                _status_label(payment.status),
            )
            for payment in statement.payments
        )
        add_data_table(
            story,
            ("Tipo", "Fecha", "Venta", "Importe", "Saldo", "Estado"),
            statement_rows,
            column_widths=(70, 80, 140, 115, 115, 90),
            centered_columns=(0, 1, 5),
        )
    return _finish_pdf(document, buffer, story)


def build_payroll_pdf(
    db: Session,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    employee_id: int | None = None,
    status: str | None = None,
) -> BytesIO:
    _validate_date_range(date_from, date_to)
    runs = payroll_service.list_runs(
        db=db,
        date_from=date_from,
        date_to=date_to,
        employee_id=employee_id,
        status=status,
    )
    active_runs = [run for run in runs if run.status == "active"]
    document, buffer, story = create_pdf_document(
        "Roles de pago base",
        _optional_period(date_from, date_to),
    )
    if not runs:
        add_empty_message(story, "Sin datos")

    add_section_heading(story, "Resumen de nómina")
    add_key_value_table(
        story,
        (
            (
                "Total bruto",
                format_money(
                    sum(
                        (run.gross_total for run in active_runs),
                        start=Decimal("0.00"),
                    )
                ),
            ),
            (
                "Total descuentos",
                format_money(
                    sum(
                        (run.total_deductions for run in active_runs),
                        start=Decimal("0.00"),
                    )
                ),
            ),
            (
                "Neto total",
                format_money(
                    sum(
                        (run.net_pay_total for run in active_runs),
                        start=Decimal("0.00"),
                    )
                ),
            ),
            ("Roles activos", len(active_runs)),
            (
                "Roles anulados",
                sum(run.status == "voided" for run in runs),
            ),
        ),
    )

    add_section_heading(story, "Detalle resumido")
    rows = []
    for run in runs:
        for item in run.items:
            if employee_id is not None and item.employee_id != employee_id:
                continue
            rows.append(
                (
                    run.payroll_number,
                    format_date(run.payroll_date),
                    item.employee_name_snapshot,
                    format_money(item.base_salary_amount),
                    format_money(item.bonus_amount),
                    format_money(item.advances_deducted_amount),
                    format_money(item.loan_deductions_amount),
                    format_money(item.other_deductions_amount),
                    format_money(item.net_pay_amount),
                    _status_label(run.status),
                )
            )
    add_data_table(
        story,
        (
            "Rol",
            "Fecha",
            "Empleado",
            "Sueldo base",
            "Bonos",
            "Anticipos",
            "Préstamos",
            "Otros desc.",
            "Neto",
            "Estado",
        ),
        rows,
        column_widths=(85, 55, 125, 70, 55, 65, 65, 65, 65, 55),
        centered_columns=(1, 9),
    )
    return _finish_pdf(document, buffer, story)


def _finish_pdf(
    document: SimpleDocTemplate,
    buffer: BytesIO,
    story: list[Flowable],
) -> BytesIO:
    document.build(
        story,
        onFirstPage=_draw_page_footer,
        onLaterPages=_draw_page_footer,
    )
    buffer.seek(0)
    return buffer


def _draw_page_footer(canvas: Canvas, document: SimpleDocTemplate) -> None:
    canvas.saveState()
    canvas.setStrokeColor(SLATE_LIGHT)
    canvas.line(
        document.leftMargin,
        10 * mm,
        PDF_PAGE_SIZE[0] - document.rightMargin,
        10 * mm,
    )
    canvas.setFillColor(SLATE)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(
        document.leftMargin,
        6 * mm,
        "Agua Activa ERP - Reporte ejecutivo de solo lectura",
    )
    canvas.drawRightString(
        PDF_PAGE_SIZE[0] - document.rightMargin,
        6 * mm,
        f"Página {document.page}",
    )
    canvas.restoreState()


def _paragraph(
    value: Any,
    style: ParagraphStyle,
    *,
    max_length: int,
) -> Paragraph:
    return Paragraph(safe_text(value, max_length=max_length), style)


def _safe_filename(filename: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]", "-", filename)
    return normalized or "reporte.pdf"


def _optional_period(
    date_from: date | None,
    date_to: date | None,
) -> str:
    if date_from is not None and date_to is not None:
        return f"{format_date(date_from)} a {format_date(date_to)}"
    if date_from is not None:
        return f"Desde {format_date(date_from)}"
    if date_to is not None:
        return f"Hasta {format_date(date_to)}"
    return "Todos los registros"


def _validate_date_range(
    date_from: date | None,
    date_to: date | None,
) -> None:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ValueError("La fecha desde no puede ser posterior a la fecha hasta.")


def _status_label(value: str | None) -> str:
    return {
        None: "-",
        "active": "Activo",
        "voided": "Anulado",
        "open": "Abierto",
        "closed": "Cerrado",
        "pending": "Pendiente",
        "paid": "Pagado",
        "warning": "Advertencia",
        "info": "Información",
        "success": "Correcto",
    }.get(value, value or "-")


def _yes_no(value: bool) -> str:
    return "Sí" if value else "No"


def _management_has_data(report: Any) -> bool:
    return any(
        (
            report.cash.cash_sessions_count,
            report.sales.active_sales_count,
            report.receivables.payments_total,
            report.operating_expenses.operating_expenses_total,
            report.purchases.active_purchases_count,
            report.production.production_batches_count,
            report.inventory.active_products_with_stock_count,
            report.routes.route_loads_count,
            report.payroll.payroll_runs_count,
        )
    )


def _management_module_rows(report: Any) -> list[tuple[str, str, Any]]:
    return [
        ("Caja", "Cuadres", report.cash.cash_sessions_count),
        ("Caja", "Total contado", format_money(report.cash.cash_total_counted)),
        ("Caja", "Caja final", format_money(report.cash.cash_final_total)),
        ("Ventas", "Ventas activas", report.sales.active_sales_count),
        ("Ventas", "Ventas totales", format_money(report.sales.sales_total)),
        (
            "Ventas",
            "Ventas anuladas",
            report.sales.voided_sales_count,
        ),
        (
            "Cartera",
            "Saldo pendiente",
            format_money(report.receivables.pending_balance_total),
        ),
        (
            "Cartera",
            "Saldo vencido",
            format_money(report.receivables.overdue_balance_total),
        ),
        (
            "Gastos operativos",
            "Total activo",
            format_money(
                report.operating_expenses.operating_expenses_total
            ),
        ),
        (
            "Gastos operativos",
            "Pendiente",
            format_money(report.operating_expenses.unpaid_expenses_total),
        ),
        (
            "Compras",
            "Total activo",
            format_money(report.purchases.purchases_total),
        ),
        (
            "Compras",
            "Pendiente",
            format_money(report.purchases.unpaid_purchases_total),
        ),
        (
            "Producción",
            "Lotes activos",
            report.production.production_batches_count,
        ),
        (
            "Producción",
            "Cantidad producida",
            format_quantity(
                report.production.production_items_total_quantity
            ),
        ),
        (
            "Inventario",
            "Stock total",
            format_quantity(report.inventory.total_stock_quantity),
        ),
        (
            "Inventario",
            "Productos con stock bajo",
            len(report.inventory.low_stock_items),
        ),
        ("Rutas", "Cargas", report.routes.route_loads_count),
        (
            "Rutas",
            "Efectivo entregado",
            format_money(report.routes.route_delivered_cash_total),
        ),
        ("Nómina", "Roles activos", report.payroll.payroll_runs_count),
        (
            "Nómina",
            "Neto calculado",
            format_money(report.payroll.net_pay_total),
        ),
    ]


def _monthly_has_data(report: Any) -> bool:
    return any(
        (
            report.cash_summary.cash_sessions_count,
            report.production_summary.production_batches_count,
            report.sales_summary.cash_sales_count,
            report.sales_summary.credit_sales_count,
            report.receivables_summary.payments_count,
            report.route_operations_summary.route_loads_count,
            report.route_operations_summary.route_returns_count,
            report.route_financial_summary.route_closures_count,
            report.route_cash_receipts_summary.receipts_count,
        )
    )


def _monthly_sections(
    report: Any,
) -> tuple[tuple[str, tuple[tuple[str, Any], ...]], ...]:
    return (
        (
            "Caja",
            (
                ("Cuadres", report.cash_summary.cash_sessions_count),
                ("Cuadres abiertos", report.cash_summary.open_cash_sessions_count),
                ("Total contado", format_money(report.cash_summary.total_counted)),
                ("Gastos", format_money(report.cash_summary.total_expenses)),
                ("Caja final", format_money(report.cash_summary.total_final)),
                (
                    "Días sin cuadre",
                    report.cash_summary.days_without_cash_session,
                ),
            ),
        ),
        (
            "Ventas y cartera",
            (
                (
                    "Venta contado",
                    format_money(report.sales_summary.cash_sales_total),
                ),
                (
                    "Venta crédito",
                    format_money(report.sales_summary.credit_sales_total),
                ),
                (
                    "Ventas anuladas",
                    report.sales_summary.voided_sales_count,
                ),
                (
                    "Crédito generado",
                    format_money(
                        report.receivables_summary.credit_sales_created_total
                    ),
                ),
                (
                    "Cobros",
                    format_money(report.receivables_summary.payments_total),
                ),
                (
                    "Crédito pendiente",
                    format_money(
                        report.receivables_summary.pending_credit_total
                    ),
                ),
            ),
        ),
        (
            "Producción",
            (
                (
                    "Producciones activas",
                    report.production_summary.active_production_batches_count,
                ),
                (
                    "Producciones anuladas",
                    report.production_summary.voided_production_batches_count,
                ),
                (
                    "Cantidad producida",
                    format_quantity(
                        report.production_summary.total_quantity_produced
                    ),
                ),
                (
                    "Merma",
                    format_quantity(
                        report.production_summary.total_quantity_waste
                    ),
                ),
                (
                    "Producción neta",
                    format_quantity(
                        report.production_summary.total_quantity_net
                    ),
                ),
            ),
        ),
        (
            "Rutas y recibos",
            (
                (
                    "Cargas activas",
                    report.route_operations_summary.active_route_loads_count,
                ),
                (
                    "Retornos activos",
                    report.route_operations_summary.active_route_returns_count,
                ),
                (
                    "Cierres activos",
                    report.route_financial_summary.active_route_closures_count,
                ),
                (
                    "Diferencia de cierres",
                    format_money(
                        report.route_financial_summary.difference_total
                    ),
                ),
                (
                    "Recibos activos",
                    report.route_cash_receipts_summary.active_receipts_count,
                ),
                (
                    "Recibido",
                    format_money(
                        report.route_cash_receipts_summary.received_amount_total
                    ),
                ),
            ),
        ),
    )


def _daily_has_data(report: Any) -> bool:
    return any(
        (
            report.cash_summary.cash_session_exists,
            report.production_summary.production_batches_count,
            report.route_loads_summary.route_loads_count,
            report.route_returns_summary.route_returns_count,
            report.route_closures_summary.route_closures_count,
            report.route_cash_receipts_summary.receipts_count,
            report.sales_summary.cash_sales_count,
            report.sales_summary.credit_sales_count,
            report.receivables_summary.payments_count,
        )
    )
