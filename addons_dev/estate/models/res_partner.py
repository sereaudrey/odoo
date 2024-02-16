from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    property_ids = fields.One2many(
        "estate.property", "buyer", string="Propriétés"
    )