from sqlalchemy import CheckConstraint, Numeric

from app.db.base import Base
import app.models  # noqa: F401


def test_initial_tables_are_registered_in_metadata() -> None:
    expected_tables = {
        "users",
        "cash_sessions",
        "denominations",
        "cash_count_items",
        "expenses",
        "correction_logs",
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
