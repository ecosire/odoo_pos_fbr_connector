# -*- coding: utf-8 -*-
# Copyright (C) ECOSIRE (PRIVATE) LIMITED.

import base64
from datetime import datetime
import io
import json
import requests
import traceback
try:
    import qrcode
except ImportError:
    qrcode = None
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    enable_fbr_config = fields.Boolean(related="company_id.enable_fbr_config", store=True)
    post_data_fbr = fields.Boolean("Post Data Successful ?")
    invoice_number = fields.Char("Invoice Number")
    fbr_request = fields.Text("FBR Request Data")
    fbr_response = fields.Text("FBR Response")
    invoice_qr_code = fields.Binary(string="QR Code")
    payment_mode = fields.Selection([
        ('1', 'Cash'),
        ('2', 'Card'),
        ('3', 'Gift Voucher'),
        ('4', 'Loyalty Card'),
        ('5', 'Mixed'),
        ('6', 'Cheque'),
        ('7', 'Sales Person'),
    ], required=True, default='1')
    invoice_datetime = fields.Datetime(string="Date ")
    service_fees = fields.Monetary(currency_field='company_currency_id', compute="_compute_service_fees", store=True)
    total_amount_without_discount = fields.Monetary(currency_field='company_currency_id', compute="_compute_service_fees", store=True)
    total_discount = fields.Monetary(currency_field='company_currency_id', compute="_compute_service_fees", store=True)
    payable_amount = fields.Monetary(currency_field='company_currency_id', compute="_compute_service_fees", store=True)
    service_fee_move_id = fields.Many2one('account.move', string="Service Fee Journal")

    @api.depends('invoice_line_ids', 'amount_total')
    def _compute_service_fees(self):
        for rec in self:
            rec.total_amount_without_discount = 0.0
            rec.service_fees = 0.0
            rec.total_discount = 0.0
            rec.service_fees = self.env.company.service_fee
            for line in rec.invoice_line_ids:
                rec.total_amount_without_discount += (line.quantity * line.price_unit)
            rec.total_discount = rec.total_amount_without_discount - rec.amount_untaxed
            rec.payable_amount = rec.amount_total

    def action_post(self):
        for invoice in self:
            if self.env.company.include_service_fees and invoice.invoice_line_ids and invoice.move_type in ('out_invoice'):
                service_fees = self.env.company.service_fee
                accounts = invoice.invoice_line_ids[0].product_id.product_tmpl_id.get_product_accounts(invoice.fiscal_position_id)
                if not accounts:
                    raise UserError(_("No account defined for this product: "))
                fbr_service_cost_account_id = self.env.ref('odoo_fbr_connector.fbr_service_cost_acc').id
                lines = invoice.line_ids.filtered(lambda x: x.name == 'Service Fees' or x.account_id.id == fbr_service_cost_account_id)
                invoice.line_ids -= lines
                self = self.with_context(check_move_validity=False)
                create_method = self.env['account.move.line'].new or self.env['account.move.line'].create
                misc_journal = self.env['account.journal'].sudo().search([('type','=','general')])
                if misc_journal:
                    move_id = self.env['account.move'].create({'journal_id': misc_journal[0].id, 'move_type':'entry'})
                    service_fee_line = create_method({
                        'account_id': accounts['income'].id,
                        'debit':  service_fees,
                        'credit': 0.0,
                        'name': 'Service Fees',
                        'display_type':'cogs'
                    })
                    move_id.line_ids += service_fee_line
                    fbr_service_cost_line = create_method({
                        'account_id': fbr_service_cost_account_id,
                        'debit':  0.0,
                        'credit': service_fees,
                        'name': 'FBR Service Cost',
                        'display_type':'cogs'
                    })
                    move_id.line_ids += fbr_service_cost_line
                    move_id.action_post()
                    invoice.sudo().write({'service_fee_move_id':move_id.id})
        res = super(AccountMove, self).action_post()
        return res

    def post_data_to_fbr(self):
        if not self:
            self = self.env['account.move'].search([])
        for account_move in self:
            now = datetime.strftime(fields.Datetime.context_timestamp(self, datetime.now()), "%Y-%m-%d %H:%M:%S")
            if not account_move.post_data_fbr and account_move.move_type in ('out_invoice', 'out_refund'):
                fbr_url = ""
                header = {"Content-Type": "application/json"}
                invoice_number = ''
                fbr_log_id = False
                if account_move.company_id.enable_fbr_config:
                    if account_move.company_id.server_type == 'sand_box':
                        fbr_url = "https://esp.fbr.gov.pk:8244/FBR/v1/api/Live/PostData"
                    else:
                        fbr_url = "https://gw.fbr.gov.pk/imsp/v1/api/Live/PostData"
                    try:
                        order_dic = {
                            "InvoiceNumber": "",
                            "USIN": account_move.name,
                            "DateTime": now,
                            "TotalBillAmount": account_move.amount_total,
                            "TotalSaleValue": account_move.amount_untaxed,
                            "TotalTaxCharged": account_move.amount_total - account_move.amount_untaxed,
                            "PaymentMode": account_move.payment_mode,
                            "InvoiceType": 1 if account_move.move_type == 'out_invoice' else 3,
                            "Discount": account_move.total_discount,
                            "FurtherTax": 0.0
                        }
                        header.update({'Authorization': account_move.company_id.account_fbr_authorization})
                        order_dic.update({'POSID': account_move.company_id.invoice_id})
                        order_dic.update({
                            "BuyerName": account_move.partner_id.name,
                            "BuyerPhoneNumber": account_move.partner_id.mobile,
                        })
                        if account_move.partner_id.cnic:
                            order_dic.update({"BuyerCNIC": account_move.partner_id.cnic})
                        if account_move.partner_id.ntn:
                            order_dic.update({"BuyerNTN": account_move.partner_id.ntn})
                        if account_move.invoice_line_ids:
                            items_list = []
                            total_qty = 0.0
                            for invoice_line in account_move.invoice_line_ids:
                                total_qty += invoice_line.quantity
                                all_tax = sum(tax.amount for tax in invoice_line.tax_ids)
                                product_name = invoice_line.product_id.name.replace(invoice_line.product_id.default_code or '', '').replace('[', '').replace(']', '')
                                line_dic = {
                                    "ItemCode": invoice_line.product_id.default_code,
                                    "ItemName": product_name,
                                    "Quantity": int(invoice_line.quantity),
                                    "PCTCode": getattr(invoice_line.product_id, 'pct_code', ''),
                                    "TaxRate": all_tax,
                                    "Discount": (invoice_line.quantity * invoice_line.price_unit) - invoice_line.price_subtotal,
                                    "SaleValue": invoice_line.price_unit,
                                    "TotalAmount": invoice_line.price_subtotal,
                                    "TaxCharged": invoice_line.price_total - invoice_line.price_subtotal,
                                    "InvoiceType": 1 if account_move.move_type == 'out_invoice' else 3,
                                    "RefUSIN": "",
                                    "FurtherTax": 0.0
                                }
                                items_list.append(line_dic)
                            order_dic.update({'Items': items_list, 'TotalQuantity': total_qty})
                            fbr_log_id = self.env['fbr.log'].create({
                                'name': account_move.name,
                                'fbr_request': json.dumps(order_dic)
                            })
                        payment_response = requests.post(fbr_url, data=json.dumps(order_dic), headers=header, verify=False, timeout=20)
                        r_json = payment_response.json()
                        invoice_number = r_json.get('InvoiceNumber')
                        if fbr_log_id:
                            fbr_log_id.write({'fbr_response': json.dumps(r_json), 'fbr_invoice_number': invoice_number, 'posted_succesfull': True})
                        account_move.write({'fbr_response': json.dumps(r_json), 'post_data_fbr': True, 'fbr_request': json.dumps(order_dic), 'invoice_number': invoice_number, 'invoice_datetime': datetime.now()})
                        if qrcode and invoice_number:
                            qr = qrcode.QRCode(
                                version=1,
                                error_correction=qrcode.constants.ERROR_CORRECT_L,
                                box_size=10,
                                border=4,
                            )
                            qr.add_data(invoice_number)
                            qr.make(fit=True)
                            img = qr.make_image()
                            temp = io.BytesIO()
                            img.save(temp, format="PNG")
                            qr_code_image = base64.b64encode(temp.getvalue())
                            account_move.invoice_qr_code = qr_code_image
                    except Exception as e:
                        values = dict(exception=str(e), traceback=traceback.format_exc())
                        if fbr_log_id:
                            fbr_log_id.write({'fbr_response': json.dumps(values), 'posted_succesfull': False})
                        account_move.write({'fbr_response': json.dumps(values), 'fbr_request': json.dumps(order_dic), 'invoice_datetime': datetime.now()}) 