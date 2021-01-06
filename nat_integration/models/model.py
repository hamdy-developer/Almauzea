from odoo import api, fields, models, _
from requests import request
import time, json, requests




class res_partner(models.Model):
    _inherit = 'res.partner'

    token = fields.Char(string="Token", required=False, readonly=True)

    @api.model
    def create(self, vals_list):
        res = super(res_partner, self).create(vals_list)
        for rec in res:
            rec.generate_token()
        return res

    def generate_token(self):
        for rec in self:
            rec.token = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase +
                                               string.digits, k=16))
        if not bool(re.search(r'\d', rec.token)):
            rec.generate_token()
