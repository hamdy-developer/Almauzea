from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError,Warning,UserError


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    discount_all = fields.Float(string="Discount for all %", required=False, )
    message = fields.Char(string="Message", required=False, )
    apply_after = fields.Date(string="Apply After", required=False, )
    discount = fields.Float(string="Discount %", required=False, )
    tolerance = fields.Float(string="Tolerance %", required=False, )
    purchase_discount_id = fields.Many2one(comodel_name="purchase.order", string="", required=False, )
    is_discount_done = fields.Boolean(string="", )

    @api.onchange('partner_id')
    def get_discount(self):
        for rec in self:
            purchase = self.env['purchase.order'].search(
                [('partner_id', '=', rec.partner_id.id), ('is_discount_done', '=', False),
                 ('apply_after', '<=', fields.Date.today())])
            if purchase:
                rec.discount_all = purchase.discount
                rec.purchase_discount_id = purchase, id

    @api.onchange('partner_id')
    def message_message(self):
        for rec in self:
            purchase = self.env['purchase.order'].search(
                [('partner_id', '=', rec.partner_id.id), ('is_discount_done', '=', False),
                 ('apply_after', '<=', fields.Date.today())])
            if purchase:
                warning_mess = {
                    'title': _('Message'),
                    'message': _('%s' % purchase.message),
                }
                return {'warning': warning_mess}


class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    stock = fields.Float(string="Stock", required=False, related="product_id.qty_available")
    avr_sales = fields.Float(string="Avr. Sales", required=False, readonly=True)
    coverage = fields.Float(string="Coverage", required=False, )
    coverage_a_o = fields.Float(string="Coverage A/O", required=False, )

    @api.onchange("product_id", 'product_qty')
    def default_avr_Sales(self):
        for rec in self:
            if rec.order_id.discount_all:
                rec.discount = rec.order_id.discount_all
            avr_sales = 0
            # yaster = datetime.today() - relativedelta(days=1)
            sale_orders = self.env['sale.order'].search([("state", '=', 'sale')])
            for order in sale_orders:
                sale_order_line = self.env['sale.order.line'].search(
                    [("order_id", '=', order.id), ('product_id', '=', rec.product_id.id)])

                for line in sale_order_line:
                    avr_sales += line.product_uom_qty
            rec.avr_sales = avr_sales
            if rec.avr_sales != 0:
                rec.coverage = rec.stock / rec.avr_sales
                rec.coverage_a_o = (rec.stock + rec.product_qty) / rec.avr_sales


class purchase_requisition(models.Model):
    _inherit = 'purchase.requisition'

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", string="Warehouse", required=False, )


class purchase_requisition_line(models.Model):
    _inherit = 'purchase.requisition.line'

    stock = fields.Float(string="Stock", required=False, related="product_id.qty_available")
    avr_sales = fields.Float(string="Avr. Sales", required=False, readonly=True)
    coverage = fields.Float(string="Coverage", required=False, )
    coverage_a_o = fields.Float(string="Coverage A/O", required=False, )

    @api.onchange("product_id", 'product_qty')
    def default_avr_Sales(self):
        for rec in self:
            avr_sales = 0
            # yaster = datetime.today() - relativedelta(days=1)
            sale_orders = self.env['sale.order'].search([("state", '=', 'sale')])
            for order in sale_orders:
                sale_order_line = self.env['sale.order.line'].search(
                    [("order_id", '=', order.id), ('product_id', '=', rec.product_id.id)])

                for line in sale_order_line:
                    avr_sales += line.product_uom_qty
            rec.avr_sales = avr_sales
            if rec.avr_sales != 0:
                rec.coverage = rec.stock / rec.avr_sales
                rec.coverage_a_o = (rec.stock + rec.product_qty) / rec.avr_sales


class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.onchange('quantity_done')
    def error_tolerance(self):
        for rec in self:
            if (1 + rec.picking_id.purchase_id.tolerance / 100) * rec.product_uom_qty < rec.quantity_done:
                raise ValidationError(_('The quantity is greater than the allowed'))
