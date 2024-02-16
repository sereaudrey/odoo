from odoo import fields, models

class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'A tag of property'
    _order = "name"
    _sql_constraints = [
        ("check_name", "UNIQUE(name)", "Ce tag existe déjà"),
    ]
    
    name = fields.Char('Nom', required=True)
    color = fields.Integer("Color Index")
    
    # Relationel
    tag_ids = fields.Many2many("estate.property","tag_ids", string="Tags")