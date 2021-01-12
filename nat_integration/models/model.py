from odoo import api, fields, models, _
from odoo.modules.module import get_module_resource
import time, json, requests
import string
import random
import re


class product_category(models.Model):
    _inherit = 'product.category'

    @api.model
    def _default_image(self):
        image_path = get_module_resource('lunch', 'static/img', 'lunch.png')
        return base64.b64encode(open(image_path, 'rb').read())

    image_1920 = fields.Image(default=_default_image)


class stock_warehouse(models.Model):
    _inherit = 'stock.warehouse'

    area_id = fields.Many2one(comodel_name="area.area", string="Area", required=False, )

class res_partner(models.Model):
    _inherit = 'res.partner'

    token = fields.Char(string="Token", required=False, readonly=True)
    shop_name = fields.Char(string="Shop Name", required=False, readonly=False)
    password = fields.Char(string="Password", required=False, readonly=False)
    area_id = fields.Many2one(comodel_name="area.area", string="Area", required=False, )

    def generate_token(self):
        for rec in self:
            rec.token = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase +
                                               string.digits, k=16))
        partner = self.env['res.partner'].sudo().search([('token', '=', rec.token), ('id', '!=', rec.id)])
        if partner:
            rec.generate_token()
        if not bool(re.search(r'\d', rec.token)):
            rec.generate_token()


class area_area(models.Model):
    _name = 'area.area'
    _rec_name = 'name'
    _description = 'areas'

    name = fields.Char(required=True )
