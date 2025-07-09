from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    strn_or_ntn = fields.Char(string="STRN/NTN")
    include_service_fees = fields.Boolean(string="Include Service Fee")
    service_fee = fields.Float(string="Service Fees")
    enable_fbr_config = fields.Boolean(string="Enable FBR Configuration")
    account_fbr_authorization = fields.Char("FBR Header Authorization")
    invoice_id = fields.Char("POSID")
    server_type = fields.Selection([
        ('sand_box', 'Sand Box'),
        ('production', 'Production')
    ], default='sand_box', string="Server Type")
    fbr_logo = fields.Binary(string="Logo")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    include_service_fees = fields.Boolean(string="Include Service Fee", related="company_id.include_service_fees", readonly=False)
    service_fee = fields.Float(string="Service Fees", related="company_id.service_fee", readonly=False)
    enable_fbr_config = fields.Boolean(string="Enable FBR Configuration", related="company_id.enable_fbr_config", readonly=False)
    account_fbr_authorization = fields.Char("FBR Header Authorization", related="company_id.account_fbr_authorization", readonly=False)
    invoice_id = fields.Char("POSID", related="company_id.invoice_id", readonly=False)
    server_type = fields.Selection(default='sand_box', string="Server Type", related="company_id.server_type", readonly=False)
    fbr_logo = fields.Binary(string="Logo", related="company_id.fbr_logo", readonly=False) 