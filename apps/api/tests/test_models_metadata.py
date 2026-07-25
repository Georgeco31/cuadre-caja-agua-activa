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
        "employee_advances",
        "employee_attendance",
        "employee_loan_payments",
        "employee_loans",
        "inventory_locations",
        "inventory_movements",
        "inventory_stocks",
        "operating_expense_categories",
        "operating_expenses",
        "payroll_item_advance_deductions",
        "payroll_item_loan_deductions",
        "payroll_items",
        "payroll_runs",
        "products",
        "price_list_items",
        "price_lists",
        "production_batches",
        "production_inventory_application_items",
        "production_inventory_applications",
        "production_items",
        "production_recipe_items",
        "production_recipes",
        "purchase_items",
        "purchases",
        "recurring_operating_expenses",
        "route_load_items",
        "route_loads",
        "route_cash_receipts",
        "route_closures",
        "route_return_items",
        "route_returns",
        "sale_items",
        "sales",
        "suppliers",
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
        Base.metadata.tables["employee_attendance"].c.hours_worked,
        Base.metadata.tables["employee_advances"].c.amount,
        Base.metadata.tables["employee_loans"].c.principal_amount,
        Base.metadata.tables["employee_loans"].c.paid_amount,
        Base.metadata.tables["employee_loans"].c.balance_amount,
        Base.metadata.tables["employee_loan_payments"].c.amount,
        Base.metadata.tables["products"].c.default_price,
        Base.metadata.tables["products"].c.cost_estimate,
        Base.metadata.tables["price_list_items"].c.unit_price,
        Base.metadata.tables["price_list_items"].c.min_quantity,
        Base.metadata.tables["sales"].c.total_amount,
        Base.metadata.tables["sales"].c.paid_amount,
        Base.metadata.tables["sales"].c.balance_amount,
        Base.metadata.tables["credit_payments"].c.amount,
        Base.metadata.tables["inventory_stocks"].c.quantity_on_hand,
        Base.metadata.tables["inventory_movements"].c.quantity,
        Base.metadata.tables["inventory_movements"].c.unit_cost,
        Base.metadata.tables["inventory_movements"].c.total_cost,
        Base.metadata.tables["production_items"].c.quantity_produced,
        Base.metadata.tables["production_items"].c.quantity_waste,
        Base.metadata.tables["production_recipes"].c.output_quantity,
        Base.metadata.tables["production_recipes"].c.estimated_material_cost,
        Base.metadata.tables["production_recipes"].c.estimated_cost_per_unit,
        Base.metadata.tables["production_recipe_items"].c.quantity_required,
        Base.metadata.tables["production_recipe_items"].c.unit_cost,
        Base.metadata.tables["production_recipe_items"].c.total_cost,
        Base.metadata.tables["production_recipe_items"].c.waste_percentage,
        Base.metadata.tables[
            "production_inventory_application_items"
        ].c.quantity_applied,
        Base.metadata.tables["route_load_items"].c.quantity_loaded,
        Base.metadata.tables["route_return_items"].c.quantity_returned,
        Base.metadata.tables["route_closures"].c.cash_sales_total,
        Base.metadata.tables["route_closures"].c.credit_sales_total,
        Base.metadata.tables["route_closures"].c.payments_total,
        Base.metadata.tables["route_closures"].c.expected_cash_total,
        Base.metadata.tables["route_closures"].c.delivered_cash_total,
        Base.metadata.tables["route_closures"].c.difference_amount,
        Base.metadata.tables["route_cash_receipts"].c.delivered_cash_total,
        Base.metadata.tables["route_cash_receipts"].c.received_amount,
        Base.metadata.tables["route_cash_receipts"].c.difference_amount,
        Base.metadata.tables["sale_items"].c.unit_price,
        Base.metadata.tables["sale_items"].c.subtotal,
        Base.metadata.tables["purchases"].c.subtotal_amount,
        Base.metadata.tables["purchases"].c.discount_amount,
        Base.metadata.tables["purchases"].c.tax_amount,
        Base.metadata.tables["purchases"].c.total_amount,
        Base.metadata.tables["purchase_items"].c.quantity,
        Base.metadata.tables["purchase_items"].c.unit_cost,
        Base.metadata.tables["purchase_items"].c.discount_amount,
        Base.metadata.tables["purchase_items"].c.tax_amount,
        Base.metadata.tables["purchase_items"].c.subtotal_amount,
        Base.metadata.tables["purchase_items"].c.total_amount,
        Base.metadata.tables["operating_expenses"].c.amount,
        Base.metadata.tables["recurring_operating_expenses"].c.amount,
        Base.metadata.tables["payroll_runs"].c.gross_total,
        Base.metadata.tables["payroll_runs"].c.total_deductions,
        Base.metadata.tables["payroll_runs"].c.net_pay_total,
        Base.metadata.tables["payroll_items"].c.base_salary_snapshot,
        Base.metadata.tables["payroll_items"].c.base_salary_amount,
        Base.metadata.tables["payroll_items"].c.gross_amount,
        Base.metadata.tables["payroll_items"].c.net_pay_amount,
        Base.metadata.tables[
            "payroll_item_advance_deductions"
        ].c.amount_deducted,
        Base.metadata.tables[
            "payroll_item_loan_deductions"
        ].c.amount_deducted,
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
    assert _foreign_key_targets("sales", "route_load_id") == {"route_loads.id"}
    assert _foreign_key_targets("sale_items", "sale_id") == {"sales.id"}
    assert _foreign_key_targets("sale_items", "product_id") == {"products.id"}
    assert _foreign_key_targets("sale_items", "price_list_id") == {
        "price_lists.id",
    }
    assert _foreign_key_targets("price_lists", "customer_id") == {
        "customers.id",
    }
    assert _foreign_key_targets("price_lists", "route_id") == {
        "delivery_routes.id",
    }
    assert _foreign_key_targets("price_list_items", "price_list_id") == {
        "price_lists.id",
    }
    assert _foreign_key_targets("price_list_items", "product_id") == {
        "products.id",
    }
    assert _foreign_key_targets("credit_payments", "sale_id") == {"sales.id"}
    assert _foreign_key_targets("credit_payments", "customer_id") == {
        "customers.id",
    }
    assert _foreign_key_targets("credit_payments", "created_by") == {"users.id"}
    assert _foreign_key_targets("credit_payments", "route_load_id") == {
        "route_loads.id",
    }
    assert _foreign_key_targets("employee_attendance", "employee_id") == {
        "employees.id",
    }
    assert _foreign_key_targets("employee_attendance", "created_by") == {
        "users.id",
    }
    assert _foreign_key_targets("employee_advances", "employee_id") == {
        "employees.id",
    }
    assert _foreign_key_targets("employee_advances", "created_by") == {
        "users.id",
    }
    assert _foreign_key_targets("employee_loans", "employee_id") == {
        "employees.id",
    }
    assert _foreign_key_targets("employee_loans", "created_by") == {
        "users.id",
    }
    assert _foreign_key_targets(
        "employee_loan_payments",
        "employee_loan_id",
    ) == {"employee_loans.id"}
    assert _foreign_key_targets("employee_loan_payments", "employee_id") == {
        "employees.id",
    }
    assert _foreign_key_targets("employee_loan_payments", "created_by") == {
        "users.id",
    }
    assert _foreign_key_targets("inventory_locations", "vehicle_id") == {
        "vehicles.id",
    }
    assert _foreign_key_targets("inventory_stocks", "product_id") == {
        "products.id",
    }
    assert _foreign_key_targets("inventory_stocks", "location_id") == {
        "inventory_locations.id",
    }
    assert _foreign_key_targets("inventory_movements", "product_id") == {
        "products.id",
    }
    assert _foreign_key_targets("inventory_movements", "location_id") == {
        "inventory_locations.id",
    }
    assert _foreign_key_targets("inventory_movements", "created_by") == {
        "users.id",
    }
    assert _foreign_key_targets("production_batches", "created_by") == {
        "users.id",
    }
    assert _foreign_key_targets("production_items", "production_batch_id") == {
        "production_batches.id",
    }
    assert _foreign_key_targets("production_items", "product_id") == {
        "products.id",
    }
    assert _foreign_key_targets("production_recipes", "output_product_id") == {
        "products.id",
    }
    assert _foreign_key_targets("production_recipes", "created_by") == {
        "users.id",
    }
    assert _foreign_key_targets(
        "production_recipe_items",
        "recipe_id",
    ) == {"production_recipes.id"}
    assert _foreign_key_targets(
        "production_recipe_items",
        "input_product_id",
    ) == {"products.id"}
    assert _foreign_key_targets(
        "production_inventory_applications",
        "production_batch_id",
    ) == {"production_batches.id"}
    assert _foreign_key_targets(
        "production_inventory_applications",
        "location_id",
    ) == {"inventory_locations.id"}
    assert _foreign_key_targets(
        "production_inventory_applications",
        "created_by",
    ) == {"users.id"}
    assert _foreign_key_targets(
        "production_inventory_application_items",
        "application_id",
    ) == {"production_inventory_applications.id"}
    assert _foreign_key_targets(
        "production_inventory_application_items",
        "production_item_id",
    ) == {"production_items.id"}
    assert _foreign_key_targets(
        "production_inventory_application_items",
        "product_id",
    ) == {"products.id"}
    assert _foreign_key_targets(
        "production_inventory_application_items",
        "inventory_movement_id",
    ) == {"inventory_movements.id"}
    assert _foreign_key_targets("route_loads", "route_id") == {
        "delivery_routes.id",
    }
    assert _foreign_key_targets("route_loads", "vehicle_id") == {"vehicles.id"}
    assert _foreign_key_targets("route_loads", "source_location_id") == {
        "inventory_locations.id",
    }
    assert _foreign_key_targets("route_loads", "destination_location_id") == {
        "inventory_locations.id",
    }
    assert _foreign_key_targets("route_loads", "created_by") == {"users.id"}
    assert _foreign_key_targets("route_load_items", "route_load_id") == {
        "route_loads.id",
    }
    assert _foreign_key_targets("route_load_items", "product_id") == {
        "products.id",
    }
    assert _foreign_key_targets("route_closures", "route_load_id") == {
        "route_loads.id",
    }
    assert _foreign_key_targets("route_closures", "route_id") == {
        "delivery_routes.id",
    }
    assert _foreign_key_targets("route_closures", "vehicle_id") == {
        "vehicles.id",
    }
    assert _foreign_key_targets("route_closures", "created_by") == {
        "users.id",
    }
    assert _foreign_key_targets(
        "route_cash_receipts",
        "route_closure_id",
    ) == {"route_closures.id"}
    assert _foreign_key_targets(
        "route_cash_receipts",
        "cash_session_id",
    ) == {"cash_sessions.id"}
    assert _foreign_key_targets(
        "route_cash_receipts",
        "route_load_id",
    ) == {"route_loads.id"}
    assert _foreign_key_targets("route_cash_receipts", "route_id") == {
        "delivery_routes.id",
    }
    assert _foreign_key_targets("route_cash_receipts", "vehicle_id") == {
        "vehicles.id",
    }
    assert _foreign_key_targets("route_cash_receipts", "created_by") == {
        "users.id",
    }
    assert _foreign_key_targets(
        "route_load_items",
        "source_exit_movement_id",
    ) == {"inventory_movements.id"}
    assert _foreign_key_targets(
        "route_load_items",
        "destination_entry_movement_id",
    ) == {"inventory_movements.id"}
    assert _foreign_key_targets("route_returns", "route_load_id") == {
        "route_loads.id",
    }
    assert _foreign_key_targets("route_returns", "route_id") == {
        "delivery_routes.id",
    }
    assert _foreign_key_targets("route_returns", "vehicle_id") == {"vehicles.id"}
    assert _foreign_key_targets("route_returns", "source_location_id") == {
        "inventory_locations.id",
    }
    assert _foreign_key_targets("route_returns", "destination_location_id") == {
        "inventory_locations.id",
    }
    assert _foreign_key_targets("route_returns", "created_by") == {"users.id"}
    assert _foreign_key_targets("route_return_items", "route_return_id") == {
        "route_returns.id",
    }
    assert _foreign_key_targets("route_return_items", "route_load_item_id") == {
        "route_load_items.id",
    }
    assert _foreign_key_targets("route_return_items", "product_id") == {
        "products.id",
    }
    assert _foreign_key_targets("purchases", "supplier_id") == {"suppliers.id"}
    assert _foreign_key_targets("purchases", "created_by") == {"users.id"}
    assert _foreign_key_targets("purchase_items", "purchase_id") == {
        "purchases.id",
    }
    assert _foreign_key_targets("purchase_items", "product_id") == {
        "products.id",
    }
    assert _foreign_key_targets("operating_expenses", "category_id") == {
        "operating_expense_categories.id",
    }
    assert _foreign_key_targets("operating_expenses", "supplier_id") == {
        "suppliers.id",
    }
    assert _foreign_key_targets(
        "operating_expenses",
        "recurring_template_id",
    ) == {"recurring_operating_expenses.id"}
    assert _foreign_key_targets("operating_expenses", "created_by") == {
        "users.id",
    }
    assert _foreign_key_targets(
        "recurring_operating_expenses",
        "category_id",
    ) == {"operating_expense_categories.id"}
    assert _foreign_key_targets(
        "recurring_operating_expenses",
        "supplier_id",
    ) == {"suppliers.id"}
    assert _foreign_key_targets(
        "recurring_operating_expenses",
        "created_by",
    ) == {"users.id"}
    assert _foreign_key_targets(
        "route_return_items",
        "source_exit_movement_id",
    ) == {"inventory_movements.id"}
    assert _foreign_key_targets(
        "route_return_items",
        "destination_entry_movement_id",
    ) == {"inventory_movements.id"}


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
        "ck_products_product_kind",
        "ck_products_unit",
    }
    assert _check_constraint_names("employees") == {
        "ck_employees_base_salary_nonnegative",
        "ck_employees_employee_type",
        "ck_employees_first_name_not_blank",
        "ck_employees_last_name_not_blank",
        "ck_employees_payment_frequency",
    }
    assert _check_constraint_names("employee_attendance") == {
        "ck_employee_attendance_hours_nonnegative",
        "ck_employee_attendance_status",
    }
    assert _check_constraint_names("employee_advances") == {
        "ck_employee_advances_amount_positive",
        "ck_employee_advances_number_not_blank",
        "ck_employee_advances_reason_not_blank",
        "ck_employee_advances_status",
        "ck_employee_advances_void_state",
    }
    assert _check_constraint_names("employee_loans") == {
        "ck_employee_loans_balance_valid",
        "ck_employee_loans_number_not_blank",
        "ck_employee_loans_paid_valid",
        "ck_employee_loans_principal_positive",
        "ck_employee_loans_reason_not_blank",
        "ck_employee_loans_status",
        "ck_employee_loans_status_balance",
        "ck_employee_loans_void_state",
    }
    assert _check_constraint_names("employee_loan_payments") == {
        "ck_employee_loan_payments_amount_positive",
        "ck_employee_loan_payments_number_not_blank",
        "ck_employee_loan_payments_status",
        "ck_employee_loan_payments_void_state",
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
        "ck_sale_items_price_source",
        "ck_sale_items_product_snapshot_not_blank",
        "ck_sale_items_quantity_positive",
        "ck_sale_items_subtotal_nonnegative",
        "ck_sale_items_unit_price_nonnegative",
    }
    assert _check_constraint_names("price_lists") == {
        "ck_price_lists_customer_route_target",
        "ck_price_lists_customer_target",
        "ck_price_lists_name_not_blank",
        "ck_price_lists_route_target",
        "ck_price_lists_type",
        "ck_price_lists_valid_dates",
    }
    assert _check_constraint_names("price_list_items") == {
        "ck_price_list_items_min_quantity_positive",
        "ck_price_list_items_price_nonnegative",
    }
    assert _check_constraint_names("credit_payments") == {
        "ck_credit_payments_amount_positive",
        "ck_credit_payments_payment_method",
        "ck_credit_payments_status",
        "ck_credit_payments_void_state",
    }
    assert _check_constraint_names("inventory_locations") == {
        "ck_inventory_locations_name_not_blank",
        "ck_inventory_locations_type",
    }
    assert _check_constraint_names("inventory_stocks") == {
        "ck_inventory_stocks_quantity_nonnegative",
    }
    assert _check_constraint_names("inventory_movements") == {
        "ck_inventory_movements_quantity_positive",
        "ck_inventory_movements_status",
        "ck_inventory_movements_total_cost_nonnegative",
        "ck_inventory_movements_type",
        "ck_inventory_movements_unit_cost_nonnegative",
        "ck_inventory_movements_void_state",
    }
    assert _check_constraint_names("production_batches") == {
        "ck_production_batches_number_not_blank",
        "ck_production_batches_status",
        "ck_production_batches_void_state",
    }
    assert _check_constraint_names("production_items") == {
        "ck_production_items_product_snapshot_not_blank",
        "ck_production_items_quantity_produced_positive",
        "ck_production_items_quantity_waste_nonnegative",
        "ck_production_items_waste_not_greater_than_produced",
    }
    assert _check_constraint_names("production_recipes") == {
        "ck_production_recipes_costs_nonnegative",
        "ck_production_recipes_name_not_blank",
        "ck_production_recipes_number_not_blank",
        "ck_production_recipes_output_quantity_positive",
        "ck_production_recipes_status",
        "ck_production_recipes_valid_dates",
        "ck_production_recipes_void_state",
    }
    assert _check_constraint_names("production_recipe_items") == {
        "ck_production_recipe_items_costs_nonnegative",
        "ck_production_recipe_items_kind_snapshot",
        "ck_production_recipe_items_name_snapshot_not_blank",
        "ck_production_recipe_items_quantity_positive",
        "ck_production_recipe_items_waste_nonnegative",
    }
    assert _check_constraint_names("production_inventory_applications") == {
        "ck_production_inventory_applications_status",
        "ck_production_inventory_applications_void_state",
    }
    assert _check_constraint_names(
        "production_inventory_application_items",
    ) == {
        "ck_production_inventory_application_items_quantity_positive",
    }
    assert _check_constraint_names("route_loads") == {
        "ck_route_loads_locations_different",
        "ck_route_loads_number_not_blank",
        "ck_route_loads_status",
        "ck_route_loads_void_state",
    }
    assert _check_constraint_names("route_load_items") == {
        "ck_route_load_items_product_snapshot_not_blank",
        "ck_route_load_items_quantity_positive",
    }
    assert _check_constraint_names("route_cash_receipts") == {
        "ck_route_cash_receipts_amounts_nonnegative",
        "ck_route_cash_receipts_closure_snapshot_not_blank",
        "ck_route_cash_receipts_difference",
        "ck_route_cash_receipts_number_not_blank",
        "ck_route_cash_receipts_route_snapshot_not_blank",
        "ck_route_cash_receipts_status",
        "ck_route_cash_receipts_vehicle_snapshot_not_blank",
        "ck_route_cash_receipts_void_state",
    }
    assert _check_constraint_names("route_returns") == {
        "ck_route_returns_locations_different",
        "ck_route_returns_number_not_blank",
        "ck_route_returns_status",
        "ck_route_returns_void_state",
    }
    assert _check_constraint_names("route_return_items") == {
        "ck_route_return_items_product_snapshot_not_blank",
        "ck_route_return_items_quantity_positive",
    }
    assert _check_constraint_names("suppliers") == {
        "ck_suppliers_identification_not_blank",
        "ck_suppliers_name_not_blank",
    }
    assert _check_constraint_names("purchases") == {
        "ck_purchases_amounts_nonnegative",
        "ck_purchases_number_not_blank",
        "ck_purchases_payment_status",
        "ck_purchases_status",
        "ck_purchases_total",
        "ck_purchases_void_state",
    }
    assert _check_constraint_names("purchase_items") == {
        "ck_purchase_items_amounts_nonnegative",
        "ck_purchase_items_product_or_description",
        "ck_purchase_items_product_snapshot",
        "ck_purchase_items_quantity_positive",
        "ck_purchase_items_subtotal",
        "ck_purchase_items_total",
    }
    assert _check_constraint_names("operating_expense_categories") == {
        "ck_operating_expense_categories_name_not_blank",
    }
    assert _check_constraint_names("operating_expenses") == {
        "ck_operating_expenses_amount_positive",
        "ck_operating_expenses_description_not_blank",
        "ck_operating_expenses_number_not_blank",
        "ck_operating_expenses_payment_method",
        "ck_operating_expenses_payment_status",
        "ck_operating_expenses_status",
        "ck_operating_expenses_void_state",
    }
    assert _check_constraint_names("recurring_operating_expenses") == {
        "ck_recurring_operating_expenses_amount_positive",
        "ck_recurring_operating_expenses_date_range",
        "ck_recurring_operating_expenses_description_not_blank",
        "ck_recurring_operating_expenses_frequency",
        "ck_recurring_operating_expenses_name_not_blank",
        "ck_recurring_operating_expenses_next_due_after_start",
        "ck_recurring_operating_expenses_next_due_before_end",
        "ck_recurring_operating_expenses_payment_method",
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
