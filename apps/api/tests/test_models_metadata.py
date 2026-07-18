from sqlalchemy import CheckConstraint, Numeric

from app.db.base import Base
import app.models  # noqa: F401


def test_initial_tables_are_registered_in_metadata() -> None:
    expected_tables = {
        "users",
        "vehicles",
        "cash_sessions",
        "denominations",
        "cash_count_items",
        "expenses",
        "correction_logs",
        "credit_payments",
        "customers",
        "delivery_routes",
        "employees",
        "products",
        "sale_items",
        "sales",
    }

    assert expected_tables == set(Base.metadata.tables.keys())


def test_unique_constraints_for_username_and_session_date() -> None:
    users = Base.metadata.tables["users"]
    cash_sessions = Base.metadata.tables["cash_sessions"]

    assert users.c.username.unique is True
    assert cash_sessions.c.session_date.unique is True


def test_money_columns_use_numeric() -> None:
    monetary_columns = [
        Base.metadata.tables["denominations"].c.value,
        Base.metadata.tables["cash_count_items"].c.subtotal,
        Base.metadata.tables["expenses"].c.amount,
        Base.metadata.tables["correction_logs"].c.previous_total,
        Base.metadata.tables["correction_logs"].c.new_total,
        Base.metadata.tables["customers"].c.credit_limit,
        Base.metadata.tables["delivery_routes"].c.expected_daily_cash,
        Base.metadata.tables["employees"].c.base_salary,
        Base.metadata.tables["products"].c.default_price,
        Base.metadata.tables["products"].c.cost_estimate,
        Base.metadata.tables["sales"].c.total_amount,
        Base.metadata.tables["sales"].c.paid_amount,
        Base.metadata.tables["sales"].c.balance_amount,
        Base.metadata.tables["credit_payments"].c.amount,
        Base.metadata.tables["sale_items"].c.unit_price,
        Base.metadata.tables["sale_items"].c.subtotal,
    ]

    for column in monetary_columns:
        assert isinstance(column.type, Numeric)


def test_required_foreign_keys_are_defined() -> None:
    assert _foreign_key_targets("cash_sessions", "created_by") == {"users.id"}
    assert _foreign_key_targets("cash_count_items", "cash_session_id") == {
        "cash_sessions.id",
    }
    assert _foreign_key_targets("cash_count_items", "denomination_id") == {
        "denominations.id",
    }
    assert _foreign_key_targets("expenses", "cash_session_id") == {
        "cash_sessions.id",
    }
    assert _foreign_key_targets("correction_logs", "cash_session_id") == {
        "cash_sessions.id",
    }
    assert _foreign_key_targets("correction_logs", "created_by") == {"users.id"}
    assert _foreign_key_targets("sales", "customer_id") == {"customers.id"}
    assert _foreign_key_targets("sales", "created_by") == {"users.id"}
    assert _foreign_key_targets("sale_items", "sale_id") == {"sales.id"}
    assert _foreign_key_targets("sale_items", "product_id") == {"products.id"}
    assert _foreign_key_targets("credit_payments", "sale_id") == {"sales.id"}
    assert _foreign_key_targets("credit_payments", "customer_id") == {
        "customers.id",
    }
    assert _foreign_key_targets("credit_payments", "created_by") == {"users.id"}


def test_model_check_constraints_are_registered() -> None:
    assert _check_constraint_names("cash_sessions") == {"ck_cash_sessions_status"}
    assert _check_constraint_names("denominations") == {
        "ck_denominations_type",
        "ck_denominations_value_positive",
    }
    assert _check_constraint_names("cash_count_items") == {
        "ck_cash_count_items_quantity_nonnegative",
        "ck_cash_count_items_subtotal_nonnegative",
    }
    assert _check_constraint_names("expenses") == {
        "ck_expenses_amount_positive",
        "ck_expenses_expense_timing",
    }
    assert _check_constraint_names("customers") == {
        "ck_customers_credit_limit_nonnegative",
        "ck_customers_customer_type",
        "ck_customers_name_not_blank",
    }
    assert _check_constraint_names("products") == {
        "ck_products_category",
        "ck_products_cost_estimate_nonnegative",
        "ck_products_default_price_nonnegative",
        "ck_products_name_not_blank",
        "ck_products_unit",
    }
    assert _check_constraint_names("employees") == {
        "ck_employees_base_salary_nonnegative",
        "ck_employees_employee_type",
        "ck_employees_first_name_not_blank",
        "ck_employees_last_name_not_blank",
        "ck_employees_payment_frequency",
    }
    assert _check_constraint_names("delivery_routes") == {
        "ck_delivery_routes_expected_cash_nonnegative",
        "ck_delivery_routes_name_not_blank",
    }
    assert _check_constraint_names("vehicles") == {
        "ck_vehicles_fuel_type",
        "ck_vehicles_name_not_blank",
        "ck_vehicles_vehicle_type",
        "ck_vehicles_year_reasonable",
    }
    assert _check_constraint_names("sales") == {
        "ck_sales_amounts_by_type",
        "ck_sales_balance_amount_nonnegative",
        "ck_sales_credit_customer_required",
        "ck_sales_credit_status",
        "ck_sales_customer_snapshot_not_blank",
        "ck_sales_paid_amount_nonnegative",
        "ck_sales_payment_method",
        "ck_sales_sale_number_not_blank",
        "ck_sales_sale_type",
        "ck_sales_status",
        "ck_sales_total_amount_nonnegative",
    }
    assert _check_constraint_names("sale_items") == {
        "ck_sale_items_product_snapshot_not_blank",
        "ck_sale_items_quantity_positive",
        "ck_sale_items_subtotal_nonnegative",
        "ck_sale_items_unit_price_nonnegative",
    }
    assert _check_constraint_names("credit_payments") == {
        "ck_credit_payments_amount_positive",
        "ck_credit_payments_payment_method",
        "ck_credit_payments_status",
        "ck_credit_payments_void_state",
    }


def _foreign_key_targets(table_name: str, column_name: str) -> set[str]:
    column = Base.metadata.tables[table_name].c[column_name]
    return {str(foreign_key.column) for foreign_key in column.foreign_keys}


def _check_constraint_names(table_name: str) -> set[str]:
    table = Base.metadata.tables[table_name]
    return {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }
