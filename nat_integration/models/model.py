from odoo import api, fields, models, _
from odoo.modules.module import get_module_resource
import time, json, requests
import string
import random
import re

class product_Unit_of_Measure(models.Model):
    _name = 'product.unit_of_measure'
    _rec_name = 'uom_id'
    _description = 'New Description'

    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',  required=True)
    price = fields.Float(string="Price",  required=True, )
    product_id = fields.Many2one(comodel_name="product.template", string="", required=True, )

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

    name = fields.Char(required=True)

class sale_order(models.Model):
    _inherit = 'sale.order'


    @api.constrains('order_line')
    def check_cancel(self):
        for rec in self:
            if len(rec.order_line.ids) == 0:
                rec.state = 'cancel'

class product_template(models.Model):
    _inherit = 'product.template'

    attachment_id = fields.Many2one(comodel_name="ir.attachment", string="image", required=True, )
    uom_ids = fields.One2many(comodel_name="product.unit_of_measure", inverse_name="product_id", string="", required=False, )

    @api.constrains("image_1920")
    def attach_image_1920(self):
        for rec in self:
            if not rec.attachment_id:
                attachment = self.env['ir.attachment'].sudo().create(
                    {"name": rec.name, "type": 'binary', 'datas': rec.image_1920})
                rec.attachment_id=attachment.id
            else:
                rec.attachment_id.datas=rec.image_1920

class product_brand(models.Model):
    _inherit = 'product.brand'

    attachment_id = fields.Many2one(comodel_name="ir.attachment", string="image", required=True, )


    @api.constrains("brand_image")
    def attachbrand_image(self):
        for rec in self:
            if not rec.attachment_id:
                attachment = self.env['ir.attachment'].sudo().create(
                    {"name": rec.name, "type": 'binary', 'datas': rec.brand_image})
                rec.attachment_id=attachment.id
            else:
                rec.attachment_id.datas=rec.brand_image

class product_template(models.Model):
    _inherit = 'product.category'

    attachment_id = fields.Many2one(comodel_name="ir.attachment", string="image", required=True, )
    image_1920 = fields.Image("Image", compute="get_image",readonly=False)
    brand_ids = fields.Many2many(comodel_name="product.brand", string="Brands" )



    @api.depends("attachment_id")
    def get_image(self):
        print('get_imageget_imageget_imageget_image')
        for rec in self:
            if rec.attachment_id:
                print("rec.attachment_id.datasrec.attachment_id.datas",rec.attachment_id.datas)
                rec.image_1920=rec.attachment_id.datas

    @api.onchange("image_1920")
    def attach_image_1920(self):
        for rec in self:
            if not rec.attachment_id:
                attachment = self.env['ir.attachment'].sudo().create(
                    {"name": rec.name, "type": 'binary', 'datas': rec.image_1920})
                rec.attachment_id=attachment.id
            else:
                rec.attachment_id.datas=rec.image_1920