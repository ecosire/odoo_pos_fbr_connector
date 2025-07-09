from odoo import fields, models

class FBRLog(models.Model):
    _name = 'fbr.log'
    _order = 'id desc'
    _description = "FBR Log"

    name = fields.Char("Invoice Ref")
    fbr_request = fields.Text("FBR Request")
    fbr_response = fields.Text("FBR Response")
    fbr_invoice_number = fields.Char("FBR Invoice Number")
    posted_succesfull = fields.Boolean("Posted Successfully ?")
    create_date = fields.Datetime("Created On", readonly=True) 