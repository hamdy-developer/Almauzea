from odoo import api, fields, models, _


class LenghtWidth(models.Model):
    _inherit = 'product.template'


    lenght=fields.Float("Lenght")
    width=fields.Float("Width")
    thickness=fields.Many2one("product.thickness",string="Thickness")
    list_price=fields.Float("Sales Price",readonly=False)
    is_dimension = fields.Boolean("Dimension",related='categ_id.is_dimension')

    @api.onchange('lenght','width','thickness',)
    def git_sale_price(self):
        for rec in self:
            if rec.is_dimension:
                if rec.lenght and rec.width and rec.thickness:
                    rec.list_price=rec.lenght*rec.width*rec.thickness.price






class LenghtWidth(models.Model):
    _inherit = 'product.product'


    @api.onchange('lenght','width','thickness',)
    def git_sale_price(self):
        for rec in self:
            if rec.is_dimension:
                if rec.lenght and rec.width and rec.thickness:
                    rec.list_price=rec.lenght*rec.width*rec.thickness.price





class ProductThickness(models.Model):
    _name = 'product.thickness'
    _description = 'product thickness'





    name=fields.Float("Thickness",required=True)
    price=fields.Float("price",required=True)

    @api.constrains('price')
    def git_product_sale_price(self):
        sale_price_template=self.env['product.template'].search([('thickness', '=', self.id)])
        for rec in sale_price_template:
            rec.git_sale_price()
        sale_price_product=self.env['product.product'].search([('thickness', '=', self.id)])
        for rec in sale_price_product:
            rec.git_sale_price()








class LenghtWidth(models.Model):
    _inherit = 'product.category'


    is_dimension=fields.Boolean("Dimension")