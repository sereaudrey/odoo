from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'An offer for property'
    _order = "price desc"
    
    price = fields.Float('Prix', required=True)
    state = fields.Selection(
        selection=[
            ('accepted', 'Acceptée'), 
            ('refused', 'Refusée')
        ],
        string='Statut',
        copy=False,
        default=False
    )
    validity = fields.Integer("Validité (jours)", default=7)
    
    # Relationel
    partner_id = fields.Many2one("res.partner", string="Acheteur", required=True)
    property_id = fields.Many2one("estate.property", string="Propriété", required=True)
    property_type_id = fields.Many2one(
        "estate.property.type", related="property_id.property_type_id", string="Type de propriété", store=True
    )
    
    # Computed
    date_deadline = fields.Date("Deadline", compute="compute_date_deadline", inverse="inverse_date_deadline")
    
    # Méthode computed
    @api.depends('validity')
    def compute_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.date_deadline = date + relativedelta(days=offer.validity)
    
    def inverse_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.validity = (offer.date_deadline - date).days
    
    # -------------------------------------------------------- Boutons -----------------------------------------------------------------------
    
    def action_accepted(self):
        if "accepted" in self.mapped("property_id.offer_ids.state"):
            raise UserError("Une offre a déjà été acceptée")
        if "solded" in self.mapped("property_id.state"):
            raise UserError("La propriété est déjà vendue")
        self.state = "accepted"
        self.mapped("property_id").write(
            {
                "state": "offer_accepted",
                "selling_price": self.price,
                "buyer": self.partner_id
            }
        )
        
    def action_refused(self):
        self.state = "refused"
    
    # -------------------------------------------------------- Contraintes --------------------------------------------------------------------
    
    @api.constrains("price")
    def check_price_offer_positive(self):
        for prop in self:
            if prop.price < 0.0 :
                raise ValidationError("Le prix de l'offre doit être supérieur à 0€")
    
    # -------------------------------------------------------- CRUD --------------------------------------------------------------------

    @api.model
    def create(self, vals):
        prop = self.env["estate.property"].browse(vals["property_id"])
        if prop.offer_ids:
            max_offer = max(prop.mapped("offer_ids.price"))
            if float_compare(vals["price"], max_offer, precision_rounding=0.01) <= 0:
                raise UserError("L'offre doit être supérieur à %.2f" % max_offer)
        prop.state ="offer_received"
        return super(PropertyOffer, self).create(vals)