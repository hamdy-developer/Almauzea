from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class purchase_order(models.Model):
    _inherit = 'purchase.order.line'

    stock = fields.Float(string="Stock", required=False, related="product_id.qty_available")
    avr_sales = fields.Float(string="Avr. Sales", required=False, readonly=True)
    coverage = fields.Float(string="Coverage", required=False, )
    coverage_a_o = fields.Float(string="Coverage A/O", required=False, )

    @api.onchange("product_id",'product_qty')
    def default_avr_Sales(self):
        for rec in self:

            avr_sales = 0
            # yaster = datetime.today() - relativedelta(days=1)
            print('yaster')
            sale_orders = self.env['sale.order'].search([("state", '=', 'sale')])
            for order in sale_orders:
                sale_order_line = self.env['sale.order.line'].search(
                    [("order_id", '=', order.id), ('product_id', '=', rec.product_id.id)])

                for line in sale_order_line:
                    avr_sales += line.product_uom_qty
            rec.avr_sales = avr_sales
            if rec.avr_sales!=0:
                rec.coverage=rec.stock/rec.avr_sales
                rec.coverage_a_o=(rec.stock+rec.product_qty)/rec.avr_sales


class res_partner(models.Model):
    _inherit = 'res.partner'

    is_verified = fields.Boolean(string="verified",  )