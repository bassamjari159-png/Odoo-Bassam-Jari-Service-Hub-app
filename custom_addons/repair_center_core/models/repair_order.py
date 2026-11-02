from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RepairOrder(models.Model):
    _name = "repair.center.order"
    _description = "Repair Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, date_received desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
        tracking=True,
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        index=True,
        tracking=True,
    )
    customer_phone = fields.Char(
        related="customer_id.phone",
        string="Customer Phone",
        readonly=True,
    )
    customer_email = fields.Char(
        related="customer_id.email",
        string="Customer Email",
        readonly=True,
    )
    device_id = fields.Many2one(
        "repair.center.device",
        string="Registered Device",
        domain="[('customer_id', '=', customer_id)]",
        tracking=True,
    )
    device_name = fields.Char(string="Device", required=True, tracking=True)
    device_serial = fields.Char(string="Serial Number", copy=False, tracking=True)
    issue_description = fields.Text(
        string="Reported Issue",
        required=True,
        tracking=True,
    )
    accessories = fields.Text(string="Received Accessories")
    device_condition = fields.Text(string="Device Condition at Reception")
    diagnosis = fields.Text(string="Technical Diagnosis", tracking=True)
    resolution = fields.Text(string="Repair Resolution", tracking=True)
    technician_id = fields.Many2one(
        "res.users",
        string="Technician",
        domain=[("share", "=", False)],
        tracking=True,
    )
    branch_id = fields.Many2one(
        "repair.center.branch",
        string="Branch",
        default=lambda self: self._default_branch(),
        tracking=True,
    )
    date_received = fields.Datetime(
        string="Received On",
        required=True,
        default=fields.Datetime.now,
        tracking=True,
    )
    estimated_completion = fields.Datetime(
        string="Expected Completion",
        tracking=True,
    )
    date_completed = fields.Datetime(string="Completed On", readonly=True)
    date_delivered = fields.Datetime(string="Delivered On", readonly=True)
    priority = fields.Selection(
        [
            ("0", "Normal"),
            ("1", "Low"),
            ("2", "High"),
            ("3", "Urgent"),
        ],
        string="Priority",
        default="0",
        tracking=True,
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("diagnosis", "Diagnosis"),
            ("approved", "Approved"),
            ("in_progress", "In Progress"),
            ("done", "Ready for Delivery"),
            ("delivered", "Delivered"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        required=True,
        copy=False,
        default="new",
        tracking=True,
    )
    line_ids = fields.One2many(
        "repair.center.order.line",
        "order_id",
        string="Services and Parts",
        copy=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.ref("base.SYP", raise_if_not_found=False)
        or self.env.company.currency_id,
        tracking=True,
    )
    amount_total = fields.Monetary(
        string="Quotation Total",
        compute="_compute_amounts",
        store=True,
        tracking=True,
    )
    amount_paid = fields.Monetary(
        string="Amount Paid",
        default=0.0,
        tracking=True,
    )
    amount_due = fields.Monetary(
        string="Amount Due",
        compute="_compute_amounts",
        store=True,
    )
    warranty_days = fields.Integer(
        string="Warranty Days",
        default=30,
        tracking=True,
    )
    warranty_expiry = fields.Date(
        string="Warranty Expiry",
        compute="_compute_warranty_expiry",
        store=True,
    )
    notes = fields.Html(string="Internal Notes")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )

    def _default_branch(self):
        return self.env["repair.center.branch"].search(
            [("company_id", "=", self.env.company.id)],
            limit=1,
        )

    @api.depends("line_ids.price_subtotal", "amount_paid")
    def _compute_amounts(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped("price_subtotal"))
            order.amount_due = order.amount_total - order.amount_paid

    @api.depends("date_delivered", "warranty_days")
    def _compute_warranty_expiry(self):
        for order in self:
            if order.date_delivered and order.warranty_days:
                delivered_date = fields.Datetime.to_datetime(
                    order.date_delivered
                ).date()
                order.warranty_expiry = delivered_date + timedelta(
                    days=order.warranty_days
                )
            else:
                order.warranty_expiry = False

    @api.onchange("device_id")
    def _onchange_device_id(self):
        if self.device_id:
            self.customer_id = self.device_id.customer_id
            self.device_name = self.device_id.name
            self.device_serial = self.device_id.serial_number

    @api.onchange("currency_id")
    def _onchange_currency_id(self):
        if self.line_ids:
            return {
                "warning": {
                    "title": _("Currency Changed"),
                    "message": _(
                        "Review the unit prices because existing lines keep their numeric values when the currency changes."
                    ),
                }
            }

    @api.constrains("amount_paid")
    def _check_amount_paid(self):
        for order in self:
            if order.amount_paid < 0:
                raise ValidationError(_("The paid amount cannot be negative."))

    @api.constrains("warranty_days")
    def _check_warranty_days(self):
        for order in self:
            if order.warranty_days < 0:
                raise ValidationError(_("Warranty days cannot be negative."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("repair.center.order")
                    or _("New")
                )
        return super().create(vals_list)

    def action_start_diagnosis(self):
        self.write({"state": "diagnosis"})

    def action_approve(self):
        self.write({"state": "approved"})

    def action_start_repair(self):
        self.write({"state": "in_progress"})

    def action_mark_done(self):
        self.write(
            {
                "state": "done",
                "date_completed": fields.Datetime.now(),
            }
        )

    def action_deliver(self):
        self.write(
            {
                "state": "delivered",
                "date_delivered": fields.Datetime.now(),
            }
        )

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_reset_to_new(self):
        self.write(
            {
                "state": "new",
                "date_completed": False,
                "date_delivered": False,
            }
        )


class RepairOrderLine(models.Model):
    _name = "repair.center.order.line"
    _description = "Repair Order Service or Part"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    order_id = fields.Many2one(
        "repair.center.order",
        required=True,
        ondelete="cascade",
    )
    line_type = fields.Selection(
        [("service", "Service"), ("part", "Spare Part")],
        string="Line Type",
        default="service",
        required=True,
    )
    service_id = fields.Many2one("repair.center.service", string="Catalog Item")
    name = fields.Char(string="Description", required=True)
    quantity = fields.Float(string="Quantity", default=1.0, required=True)
    unit_price = fields.Monetary(string="Unit Price", default=0.0, required=True)
    discount = fields.Float(string="Discount %", default=0.0)
    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute="_compute_price_subtotal",
        store=True,
    )
    currency_id = fields.Many2one(
        related="order_id.currency_id",
        readonly=True,
    )

    @api.depends("quantity", "unit_price", "discount")
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = (
                line.quantity * line.unit_price * (1 - line.discount / 100)
            )

    @api.onchange("service_id")
    def _onchange_service_id(self):
        if self.service_id:
            if (
                self.order_id.currency_id
                and self.service_id.currency_id != self.order_id.currency_id
            ):
                self.service_id = False
                return {
                    "warning": {
                        "title": _("Different Currency"),
                        "message": _(
                            "Choose a catalog item priced in the same currency as the repair order."
                        ),
                    }
                }
            self.name = self.service_id.name
            self.unit_price = self.service_id.list_price
            self.line_type = (
                "part" if self.service_id.service_type == "part" else "service"
            )

    @api.constrains("quantity", "discount")
    def _check_line_values(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_("Quantity must be greater than zero."))
            if not 0 <= line.discount <= 100:
                raise ValidationError(_("Discount must be between 0 and 100."))

