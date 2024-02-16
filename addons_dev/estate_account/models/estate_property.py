from odoo import models
from odoo import Command

class Property(models.Model):
    _inherit = "estate.property"
    
    def action_solded(self):
        journal = self.env['account.journal'].search([("type", "=","sale")], limit=1)
        for prop in self :
            self.env['account.move'].create(
                {
                    "partner_id": prop.buyer.id,
                    "move_type": "out_invoice",
                    "journal_id": journal.id,
                    "line_ids": [
                        Command.create(
                            {
                                "name": prop.name,
                                "quantity": 1.0,
                                "price_unit": prop.selling_price * 6.0 / 100.0,
                            },
                            
                        ),
                        Command.create(
                            {
                                "name": "Frais administratifs",
                                "quantity": 1.0,
                                "price_unit": 100.0,
                            }
                        )
                    ],
                }
            )
        return super(Property, self).action_solded()