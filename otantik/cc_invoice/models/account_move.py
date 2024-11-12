import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from datetime import datetime, timedelta


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = "account.move"

    cc_qr = fields.Char(string='Zatka QR Code')
    cc_invoice_datetime = fields.Datetime(string='Zatka Confirmation Datetime')

    def _fix_null_cc_invoice_datetime(self):
        all_out_invoice =self.env['account.move'].search([('move_type', '=', 'out_invoice')or('move_type', '=', 'out_refund')])

        # [('move_type', '=', 'out_invoice')]

        for out_invoice in all_out_invoice:
            if out_invoice.state == "posted" and not out_invoice.cc_invoice_datetime:
                out_invoice.cc_invoice_datetime = out_invoice.invoice_date
            if out_invoice.state == "posted" and not out_invoice.cc_qr:
                out_invoice._compute_cc_zatka()
            if out_invoice.state == "posted" :
                out_invoice._compute_cc_zatka()



    def _compute_cc_zatka(self):

        # "test vat663355441122021-12-04T07:53:14+03:001.150.15"
        # doc.company_id.name,doc.company_id.vat,doc.invoice_date,doc.amount_tax_signed,doc.amount_total
        for record in self:
            if record.state == "posted":
                def get_qr_encoding(tag, field):
                    company_name_byte_array = field.encode('UTF-8')
                    company_name_tag_encoding = tag.to_bytes(length=1, byteorder='big')
                    company_name_length_encoding = len(company_name_byte_array).to_bytes(length=1, byteorder='big')
                    return company_name_tag_encoding + company_name_length_encoding + company_name_byte_array
                if not self.company_id.vat :
                    raise UserError(_('Please set VAt number for th company.'))
                if not record.cc_invoice_datetime:
                    record.cc_invoice_datetime = fields.Datetime.now()
                company_name = get_qr_encoding(1, self.company_id.name)
                company_vat = get_qr_encoding(2, self.company_id.vat)
                invoice_date = get_qr_encoding(3, self.cc_invoice_datetime.isoformat())
                amount_total = get_qr_encoding(4, str(self.amount_total))
                amount_tax_signed = get_qr_encoding(5, str(self.amount_tax_signed))
                str_to_encode = company_name + company_vat + invoice_date + amount_total + amount_tax_signed
                qr_code_str = base64.b64encode(str_to_encode).decode('UTF-8')
                record.cc_qr = qr_code_str
