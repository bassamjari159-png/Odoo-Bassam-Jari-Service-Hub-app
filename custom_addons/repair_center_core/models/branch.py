from odoo import fields, models


class RepairBranch(models.Model):
    _name = "repair.center.branch"
    _description = "Service Branch"
    _order = "sequence, name"

    sequence = fields.Integer(default=10)
    name = fields.Char(string="Branch Name", required=True, translate=True)
    code = fields.Char(string="Branch Code", required=True, copy=False)
    manager_id = fields.Many2one(
        "res.users",
        string="Branch Manager",
        domain=[("share", "=", False)],
    )
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    address = fields.Text(string="Address")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    _code_company_unique = models.Constraint(
        "UNIQUE(code, company_id)",
        "The branch code must be unique per company.",
    )

