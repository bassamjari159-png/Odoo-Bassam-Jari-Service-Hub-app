from odoo import api, fields, models


class RepairDashboard(models.Model):
    _name = "repair.center.dashboard"
    _description = "Service Company Dashboard"

    name = fields.Char(default="Company Overview", required=True, translate=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    brand_name = fields.Char(related="company_id.repair_brand_name", readonly=True)
    owner_name = fields.Char(related="company_id.repair_owner_name", readonly=True)
    tagline = fields.Char(related="company_id.repair_tagline", readonly=True)
    syp_currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.ref("base.SYP", raise_if_not_found=False),
        readonly=True,
    )
    usd_currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.ref("base.USD", raise_if_not_found=False),
        readonly=True,
    )
    total_orders = fields.Integer(compute="_compute_metrics")
    active_orders = fields.Integer(compute="_compute_metrics")
    ready_orders = fields.Integer(compute="_compute_metrics")
    delivered_orders = fields.Integer(compute="_compute_metrics")
    total_customers = fields.Integer(compute="_compute_metrics")
    total_devices = fields.Integer(compute="_compute_metrics")
    total_revenue_syp = fields.Monetary(
        string="Revenue in Syrian Pounds",
        currency_field="syp_currency_id",
        compute="_compute_metrics",
    )
    outstanding_amount_syp = fields.Monetary(
        string="Outstanding in Syrian Pounds",
        currency_field="syp_currency_id",
        compute="_compute_metrics",
    )
    total_revenue_usd = fields.Monetary(
        string="Revenue in US Dollars",
        currency_field="usd_currency_id",
        compute="_compute_metrics",
    )
    outstanding_amount_usd = fields.Monetary(
        string="Outstanding in US Dollars",
        currency_field="usd_currency_id",
        compute="_compute_metrics",
    )

    @api.depends("company_id")
    def _compute_metrics(self):
        order_model = self.env["repair.center.order"]
        device_model = self.env["repair.center.device"]
        for dashboard in self:
            company_domain = [("company_id", "=", dashboard.company_id.id)]
            orders = order_model.search(company_domain)
            dashboard.total_orders = len(orders)
            dashboard.active_orders = len(
                orders.filtered(
                    lambda order: order.state
                    in {"new", "diagnosis", "approved", "in_progress"}
                )
            )
            dashboard.ready_orders = len(
                orders.filtered(lambda order: order.state == "done")
            )
            dashboard.delivered_orders = len(
                orders.filtered(lambda order: order.state == "delivered")
            )
            dashboard.total_customers = len(orders.mapped("customer_id"))
            dashboard.total_devices = device_model.search_count(company_domain)
            syp_orders = orders.filtered(lambda order: order.currency_id.name == "SYP")
            usd_orders = orders.filtered(lambda order: order.currency_id.name == "USD")
            dashboard.total_revenue_syp = sum(syp_orders.mapped("amount_total"))
            dashboard.outstanding_amount_syp = sum(syp_orders.mapped("amount_due"))
            dashboard.total_revenue_usd = sum(usd_orders.mapped("amount_total"))
            dashboard.outstanding_amount_usd = sum(usd_orders.mapped("amount_due"))

    def _orders_action(self, domain=None):
        action = self.env.ref(
            "repair_center_core.action_repair_center_order"
        ).read()[0]
        action["domain"] = domain or []
        return action

    def action_all_orders(self):
        return self._orders_action()

    def action_active_orders(self):
        return self._orders_action(
            [("state", "in", ["new", "diagnosis", "approved", "in_progress"])]
        )

    def action_ready_orders(self):
        return self._orders_action([("state", "=", "done")])

    def action_delivered_orders(self):
        return self._orders_action([("state", "=", "delivered")])

