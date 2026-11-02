from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    repair_brand_name = fields.Char(
        string="Service Brand",
        default="BASSAM JARI Service Hub",
    )
    repair_owner_name = fields.Char(
        string="Founder / General Manager",
        default="Engineer BASSAM JARI",
    )
    repair_tagline = fields.Char(
        string="Service Tagline",
        default="Smart service. Trusted results.",
    )
    repair_support_phone = fields.Char(string="Support Phone")
    repair_support_email = fields.Char(string="Support Email")

