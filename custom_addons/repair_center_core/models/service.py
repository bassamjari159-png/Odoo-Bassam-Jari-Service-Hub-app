from odoo import fields, models


class RepairService(models.Model):
    _name = "repair.center.service"
    _description = "Service Catalog"
    _order = "sequence, name"

    sequence = fields.Integer(default=10)
    name = fields.Char(string="Service Name", required=True, translate=True)
    code = fields.Char(string="Service Code", required=True, copy=False)
    service_type = fields.Selection(
        [
            ("diagnosis", "Diagnosis"),
            ("repair", "Repair"),
            ("installation", "Installation"),
            ("maintenance", "Maintenance"),
            ("part", "Spare Part"),
            ("other", "Other"),
        ],
        string="Type",
        default="repair",
        required=True,
    )
    list_price = fields.Monetary(string="Sales Price", default=0.0)
    standard_cost = fields.Monetary(string="Internal Cost", default=0.0)
    expected_hours = fields.Float(string="Expected Hours", default=1.0)
    warranty_days = fields.Integer(string="Warranty Days", default=30)
    description = fields.Text(string="Description", translate=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.ref("base.SYP", raise_if_not_found=False)
        or self.env.company.currency_id,
    )

    _code_company_unique = models.Constraint(
        "UNIQUE(code, company_id)",
        "The service code must be unique per company.",
    )

