from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pct_code = fields.Char("PCT Code") 