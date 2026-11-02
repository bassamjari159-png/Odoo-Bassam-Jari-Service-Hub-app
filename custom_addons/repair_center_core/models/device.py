from odoo import api, fields, models


class RepairDevice(models.Model):
    _name = "repair.center.device"
    _description = "Customer Device"
    _order = "name, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Device Name", required=True, tracking=True)
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        index=True,
        tracking=True,
    )
    device_type = fields.Selection(
        [
            ("phone", "Phone"),
            ("tablet", "Tablet"),
            ("laptop", "Laptop"),
            ("desktop", "Desktop"),
            ("printer", "Printer"),
            ("network", "Network Device"),
            ("other", "Other"),
        ],
        string="Device Type",
        default="phone",
        required=True,
        tracking=True,
    )
    brand = fields.Char(string="Brand")
    model = fields.Char(string="Model")
    serial_number = fields.Char(string="Serial Number", copy=False, index=True)
    imei = fields.Char(string="IMEI", copy=False, index=True)
    color = fields.Char(string="Color")
    purchase_date = fields.Date(string="Purchase Date")
    notes = fields.Html(string="Device Notes")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    repair_count = fields.Integer(compute="_compute_repair_count")

    @api.depends("customer_id")
    def _compute_repair_count(self):
        order_model = self.env["repair.center.order"]
        for device in self:
            device.repair_count = order_model.search_count(
                [("device_id", "=", device.id)]
            )

    def action_view_repairs(self):
        self.ensure_one()
        action = self.env.ref(
            "repair_center_core.action_repair_center_order"
        ).read()[0]
        action["domain"] = [("device_id", "=", self.id)]
        action["context"] = {
            "default_device_id": self.id,
            "default_customer_id": self.customer_id.id,
            "default_device_name": self.name,
            "default_device_serial": self.serial_number,
        }
        return action

