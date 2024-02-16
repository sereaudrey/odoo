from datetime import timedelta
from datetime import datetime
from odoo import api,fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

class Property(models.Model):
    
    # -------------------------------------------------------- Attributs privés -----------------------------------------------------------------
    
    _name = 'estate.property'
    _description = 'A property'
    _order = "id desc"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Le nom de la proriété existe déjà. Veuillez en choisir un autre')
    ]
    
    # ---------------------------------------------------------Méthodes --------------------------------------------------------------------------
    
    def get_title(property):
        for record in property:
            return record.title
        
    # -------------------------------------------------------- Déclaration des fields ------------------------------------------------------------
    
    name = fields.Char(string='Titre', default=get_title, required=True)
    description = fields.Text()
    postcode = fields.Char(string='Code postal')
    date_availability = fields.Date(string='Date de disponibilité', copy=False, default=lambda s:fields.datetime.now()+timedelta(days=90))
    expected_price =fields.Float(string='Prix attendu', required=True)
    selling_price = fields.Float(string='Prix de vente', readonly=True, copy=False)
    bedrooms = fields.Integer(string='Chambres', default=2)
    living_area = fields.Integer(string='Surface habitable')
    facades = fields.Integer(string='Nombre de pièces')
    garage = fields.Boolean()
    garden = fields.Boolean(string='Jardin')
    garden_area = fields.Integer(string='Surface du jardin')
    garden_orientation = fields.Selection(
        string='Orientation du jardin',
        selection=[
            ('north', 'Nord'), 
            ('south', 'Sud'), 
            ('east', 'Est'), 
            ('west', 'Ouest')],
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        string='Statut',
        selection=[
            ('new', 'Nouveau'), 
            ('offer_received', 'Offre reçue'), 
            ('offer_accepted', 'Offre acceptée'), 
            ('solded', 'Vendue'), 
            ('canceled', 'Annulée')],
        required=True,
        default='new'
    )
    
    # -------------------------------------------------------- Relationnel -----------------------------------------------------------------
    
    property_type_id = fields.Many2one("estate.property.type", string="Type de propriété")
    salesman = fields.Many2one("res.users", string="Vendeur", default=lambda s:s.env.user)
    buyer = fields.Many2one("res.partner", string="Acheteur", copy= False)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer","property_id", string="Propriétés")
    
    # -------------------------------------------------------- Computed ---------------------------------------------------------------------

    total_area = fields.Integer(compute="compute_total_area", string="Surface totale")
    best_price = fields.Float(compute="compute_best_price", string="Meilleure offre")
    
    # -------------------------------------------------------- Méthodes computed -------------------------------------------------------------
    
    @api.depends("living_area", "garden_area")
    def compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
    
    @api.depends("offer_ids.price")
    def compute_best_price(self):
        for record in self:
            # if not record.offer_ids :
            #     return 0.00
            # else:
            record.best_price = max(record.offer_ids.mapped('price')) if record.offer_ids else 0.0
    
    # -------------------------------------------------------- Onchange ---------------------------------------------------------------------
    
    @api.onchange("garden")
    def onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False
            
    # -------------------------------------------------------- Boutons -----------------------------------------------------------------------
    
    def action_canceled(self):
        if "solded" in self.mapped("state"):
            raise UserError("Une propriété vendue ne peut pas être annulée")
        else:
            self.state = "canceled"
    
    def action_solded(self):
        if "canceled" in self.mapped("state"):
            raise UserError("Une propriété annulée ne peut pas être vendue")
        else:
            self.state = "solded"  
    
    # -------------------------------------------------------- Contraintes --------------------------------------------------------------------
    
    @api.constrains("expected_price", "selling_price")
    def check_prices_positive(self):
        for prop in self:
            if prop.expected_price <= 0.0 and prop.selling_price <= 0.0:
                raise ValidationError("Le prix attendu et le prix de vente doivent être supérieur à 0€")
            if (
                not float_is_zero(prop.selling_price, precision_rounding=0.01)
                and float_compare(prop.selling_price, prop.expected_price * 90.0 /100.0, precision_rounding = 0.01) < 0 
            ):
                raise ValidationError("Le prix de vente ne doit pas être inférieur a 90% du prix attendu")
            
    # -------------------------------------------------------- CRUD ----------------------------------------------------------------------------
    
    def unlink(self):
        if not set(self.mapped("state"))  <= {"new", "canceled"}:
            raise UserError("Seule une propriété avec un statut 'nouveau' ou 'annulée' peut être supprimée")
        return super().unlink()
