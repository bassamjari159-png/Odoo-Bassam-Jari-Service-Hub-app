from datetime import timedelta

from odoo import fields


company = env.ref("base.main_company")
syp = env.ref("base.SYP")
usd = env.ref("base.USD")
branch = env.ref("repair_center_core.branch_main")
customer = env.ref("base.res_partner_2")
service = env.ref("repair_center_core.service_general_repair")

device = env["repair.center.device"].create(
    {
        "name": "Automated Test Device",
        "customer_id": customer.id,
        "device_type": "phone",
        "brand": "Test Brand",
        "model": "T-19",
        "serial_number": "TEST-ODOO-19",
        "company_id": company.id,
    }
)

order = env["repair.center.order"].create(
    {
        "customer_id": customer.id,
        "device_id": device.id,
        "device_name": device.name,
        "device_serial": device.serial_number,
        "issue_description": "Automated verification issue",
        "branch_id": branch.id,
        "company_id": company.id,
        "currency_id": syp.id,
        "amount_paid": 10.0,
        "warranty_days": 30,
    }
)

env["repair.center.order.line"].create(
    {
        "order_id": order.id,
        "service_id": service.id,
        "name": service.name,
        "quantity": 2.0,
        "unit_price": 35.0,
        "discount": 10.0,
    }
)

assert order.amount_total == 63.0, order.amount_total
assert order.amount_due == 53.0, order.amount_due

order.action_start_diagnosis()
order.action_approve()
order.action_start_repair()
order.action_mark_done()
assert order.state == "done"
assert order.date_completed

order.action_deliver()
assert order.state == "delivered"
assert order.date_delivered
expected_expiry = fields.Datetime.to_datetime(order.date_delivered).date() + timedelta(
    days=30
)
assert order.warranty_expiry == expected_expiry

usd_order = env["repair.center.order"].create(
    {
        "customer_id": customer.id,
        "device_name": "USD Test Device",
        "issue_description": "Verify USD pricing",
        "branch_id": branch.id,
        "company_id": company.id,
        "currency_id": usd.id,
    }
)
env["repair.center.order.line"].create(
    {
        "order_id": usd_order.id,
        "name": "USD-priced service",
        "quantity": 1.0,
        "unit_price": 20.0,
    }
)
assert usd_order.currency_id == usd
assert usd_order.amount_total == 20.0

dashboard = env.ref("repair_center_core.dashboard_main")
dashboard._compute_metrics()
assert dashboard.total_revenue_syp >= 63.0
assert dashboard.total_revenue_usd >= 20.0

env.cr.rollback()
print("Core workflow, SYP/USD totals, payment balance, and warranty verified successfully.")
