# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import requests
import base64
import json
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

HEADERS = {'Content-Type': 'application/json'}


class NatApi(http.Controller):

    def get_customer(self, token):
        customer = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
        return customer

    def get_subcategory(self, category_id):
        categorys = request.env['product.category'].sudo().search([('parent_id', '=', category_id.id)])
        data = []
        for category in categorys:
            data.append(self.category_data(category))
        return data

    def category_data(self, category):
        base_path = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        image_url = "Null"
        if category.attachment_id.local_url:
            image_url = base_path + category.attachment_id.local_url
        brand = "Null"

        return {'id': category.id, 'name': category.name, 'image': image_url,
                'subcategory': self.get_subcategory(category), 'parent_id': category.parent_id.id or "Null"}

    def product_data(self, product):
        base_path = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        image_url = "Null"
        if product.attachment_id.local_url:
            image_url = base_path + product.attachment_id.local_url
        brand = "Null"
        if product.brand_id:
            brand = {'id': product.brand_id.id, 'name': product.brand_id.name}
        units_of_measure = []
        for uom in product.uom_ids:
            units_of_measure.append(
                {'id': uom.uom_ids.uom_id.id, 'name': uom.uom_ids.uom_id.name, 'price': round(uom.uom_ids.price,2)})
        return {'id': product.id, 'name': product.name, 'image': image_url,
                'default_Price': round(product.list_price,2), 'Barcode': product.barcode,
                'default_Unit_of_Measure': {'id': product.uom_id.id, 'name': product.uom_id.name},
                'brand': brand, 'units_of_measure': units_of_measure}

    def brand_data(self, brand):
        base_path = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        image_url = "Null"
        if brand.attachment_id.local_url:
            image_url = base_path + brand.attachment_id.local_url
        return {'id': brand.id, 'name': brand.name, 'image': image_url, }

    def best_seller(self):
        stock_quant = request.env['stock.quant'].sudo().search(
            [('location_id', '=', request.env.ref('stock.stock_location_customers').id)], order="inventory_quantity",
            limit=10)
        data = []
        for stock in stock_quant:
            data.append(self.product_data(stock.product_id))
        return data

    def sale_order_data(self, sale_order):
        line_data=[]
        for line in sale_order.order_line:
            base_path = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            image_url = "Null"
            if line.product_id.attachment_id.local_url:
                image_url = base_path + line.product_id.attachment_id.local_url
            line_data.append({"id": line.id,
                              "product": {"id": line.product_id.id, "name": line.product_id.name,
                                          "image": image_url}, "quantity": line.product_uom_qty,
                              "units_of_measure": {"id": line.product_uom.id,
                                                   "name": line.product_uom.name},
                              "subtotal": line.price_subtotal, })

        return  {"id": sale_order.id, "name": sale_order.name, "date": sale_order.date_order,
                "total_untax": round(sale_order.amount_untaxed,2), "tax": round(sale_order.amount_tax,2),
                "total": round(sale_order.amount_total,2), "lines": line_data}

    @http.route('/api/check/customer', type='json', methods=['GET'], auth='public', sitemap=False)
    def check_customer(self, **kw):
        """{
            "params": {
                "mobile_number": "0100"
            }
        }"""
        if not kw:
            response = {"code": 401, "message": "All required data are missing!"}
            return response
        else:
            if kw.get('mobile_number', False):
                custome = request.env['res.partner'].sudo().search([('phone', '=', kw.get('mobile_number'))],
                                                                   limit=1)

                if custome:
                    response = {"code": 200, "message": "Custome already exist", "data": True}
                    return response
                else:
                    response = {"code": 200, "message": "Custome Not Exist", "data": False}
                return response
            else:
                response = {"code": 401, "message": "All required data are missing!"}
                return response

    @http.route('/api/get/area', type='json', methods=['POST'], auth='public', sitemap=False)
    def get_area(self,**kw):
        data = []
        ereas = request.env['area.area'].sudo().search([])
        for erea in ereas:
            data.append({'id': erea.id, 'name': erea.name})
        response = {"code": 200, "message": "All areas", "data": data}
        return response

    @http.route('/api/create/customer', type='json', methods=['POST'], auth='public', sitemap=False)
    def create_customer(self, **kw):
        """{
                    "params": {
                        "name": "tttttttt",
                        "password": "123",
                        "shop_name": "shop_name",
                        "email": "email",
                        "mobile": "0100",
                        "area": "city",
                        "zip": "zip",
                        "street": "street",
                        "street2": "street2"
                    }
                }"""
        if not kw:
            response = {"code": 401, "message": "All required data are missing!"}
            return response
        else:
            customer = request.env['res.partner'].sudo().search([('phone', '=', kw.get('mobile'))], limit=1)
            area = request.env['area.area'].sudo().search([('id', '=', int(kw.get('area')))], limit=1)
            area_id = False
            if area:
                area_id = area.id
            if customer:
                response = {"code": 400, "message": "Custome already exist", "data": True}
                return response

            if kw.get('name', False) and kw.get('password', False):
                vals = {
                    'is_company': False,
                    'customer_rank': 1,
                    'type': 'private',
                    'name': kw.get('name'),
                    'shop_name': kw.get('shop_name'),
                    'email': kw.get('email'),
                    'phone': kw.get('mobile'),
                    'area_id': area_id,
                    'zip': kw.get('zip'),
                    'street': kw.get('street'),
                    'street2': kw.get('street2'),
                    'password': kw.get('password'),
                }
                new_customer = request.env['res.partner'].sudo().create(vals)
                new_customer.sudo().generate_token()
                area_data = {}
                if new_customer.area_id:
                    area_data = {'id': new_customer.area_id.id, 'name': new_customer.area_id.name}

                valus = {
                    "token": new_customer.token,
                    "password": new_customer.password,
                    "name": new_customer.name,
                    "shop_name": new_customer.shop_name,
                    "email": new_customer.email,
                    "mobile": new_customer.phone,
                    "area": area_data,
                    "zip": new_customer.zip,
                    "street": new_customer.street,
                    "street2": new_customer.street2
                }
                response = {"code": 200, "message": "create new customer", "data": valus}
                return response
            else:
                response = {"code": 401, "message": "password or name is missing!"}
                return response

    @http.route('/api/edit/customer', type='json', methods=['POST'], auth='public', sitemap=False)
    def edit_customer(self, **kw):
        """{
                    "params": {
                        "token":"token",
                        "name": "tttttttt",
                        "password": "123",
                        "shop_name": "shop_name",
                        "email": "email",
                        "mobile": "0100",
                        "area": area.id
                        "zip": "zip",
                        "street": "street",
                        "street2": "street2"
                    }
                }"""
        if not kw:
            response = {"result": {"code": 401, "message": "All required data are missing!"}}
            return response
        else:
            area = request.env['area.area'].sudo().search([('id', '=', int(kw.get('area')))], limit=1)
            area_id = False
            if area:
                area_id = area.id
            if kw.get('name', False) and kw.get('password', False) and kw.get('token', False):
                vals = {
                    'is_company': False,
                    'customer_rank': 1,
                    'type': 'private',
                    'name': kw.get('name'),
                    'shop_name': kw.get('shop_name'),
                    'email': kw.get('email'),
                    'phone': kw.get('mobile'),
                    'area_id': area_id,
                    'zip': kw.get('zip'),
                    'street': kw.get('street'),
                    'street2': kw.get('street2'),
                    'password': kw.get('password'),
                }
                customer = self.get_customer(kw.get('token'))
                if customer:
                    customer.sudo().write(vals)
                    response = {"code": 200, "message": "Edit customer data", "data": kw}
                    return response
                else:
                    response = {"code": 401, "token": "missing"}
                    return response
            else:
                response = {"code": 401, "message": "password or name or token is missing!"}
                return response

    @http.route('/api/delete/customer', type='json', methods=['POST'], auth='public', sitemap=False)
    def delete_customer(self, **kw):
        """{
                    "params": {
                        "token":"token",
                    }
                }"""
        if not kw:
            response = {"code": 401, "message": "All required data are missing!"}
            return response
        else:
            if kw.get('token', False):
                customer = self.get_customer(kw.get('token'))
                if customer:
                    customer.sudo().unlink()
                    response = {"code": 200, "message": "Customer deleted", "data": {}}
                    return response
                else:
                    response = {"code": 401, "token": "Not Exist"}
                    return response
            else:
                response = {"code": 401, "message": "token is missing!"}
                return response

    @http.route('/api/login/customer', type='json', methods=['POST'], auth='public', sitemap=False)
    def login_customer(self, **kw):
        """{
                    "params": {
                        "mobile": "0100",
                        "password": "123",
                    }
                }"""
        if not kw:
            response = {"code": 401, "message": "All required data are missing!"}
            return response
        else:
            if kw.get('mobile', False) and kw.get('password', False):
                customer = request.env['res.partner'].sudo().search(
                    [('password', '=', kw.get('password')), ('phone', '=', kw.get('mobile'))], limit=1)
                if customer:
                    area_data = {}
                    if customer.area_id:
                        area_data = {'id': customer.area_id.id, 'name': customer.area_id.name}
                    customer.sudo().generate_token()
                    valus = {
                        "token": customer.token,
                        "password": customer.password,
                        "name": customer.name,
                        "shop_name": customer.shop_name,
                        "email": customer.email,
                        "mobile": customer.phone,
                        "area": area_data,
                        "zip": customer.zip,
                        "street": customer.street,
                        "street2": customer.street2
                    }
                    response = {"code": 200, "message": "login", "data": valus}
                    return response
                else:
                    response = {"code": 401, "message": "Customer Not Exist"}
                    return response
            else:
                response = {"code": 401, "message": "mobile or password is missing!"}
                return response

    @http.route('/api/reset/password', type='json', methods=['POST'], auth='public', sitemap=False)
    def reset_password(self, **kw):
        """{
                    "params": {
                        "mobile": "0100",
                        "password": "123",
                    }
                }"""
        if not kw:
            response = {"code": 401, "message": "All required data are missing!"}
            return response
        else:
            if kw.get('mobile', False) and kw.get('password', False):
                customer = request.env['res.partner'].sudo().search(
                    [('phone', '=', kw.get('mobile'))], limit=1)
                if customer:
                    customer.sudo().generate_token()
                    customer.sudo().password = kw.get('password')
                    area_data = {}
                    if customer.area_id:
                        area_data = {'id': customer.area_id.id, 'name': customer.area_id.name}
                    valus = {
                        "token": customer.token,
                        "password": customer.password,
                        "name": customer.name,
                        "shop_name": customer.shop_name,
                        "email": customer.email,
                        "mobile": customer.phone,
                        "area": area_data,
                        "zip": customer.zip,
                        "street": customer.street,
                        "street2": customer.street2
                    }
                    response = {"code": 200, "message": "login", "data": valus}
                    return response
                else:
                    response = {"code": 401, "message": "Customer Not Exist"}
                    return response
            else:
                response = {"code": 401, "message": "mobile or password is missing!"}
                return response

    @http.route('/api/get/brand', type='json', methods=['POST'], auth='public', sitemap=False)
    def get_brand(self, **kw):
        """{
                    "params": {
                        "token":"token",
                        "category":"category_id"
                    }
                }"""
        if not kw:
            response = {"code": 401, "message": "token is missing!"}
            return response
        else:
            if kw.get('token', False):
                customer = self.get_customer(kw.get('token'))
                if customer:
                    category = request.env['product.category'].sudo().search(
                        [('id', '=', int(kw.get('category')))])
                    data = [{"id": 0, "name": "all"}]
                    for brand in category.brand_ids:
                        data.append(self.brand_data(brand))
                    response = {"code": 200, "message": "All brands", "data": data}
                    return response
                else:
                    response = {"code": 401, "message": "token is missing!"}
                    return response

    @http.route('/api/get/category', type='json', methods=['POST'], auth='public', sitemap=False)
    def get_category(self, **kw):
        """{
                    "params": {
                        "token":"token",
                    }
                }"""
        if not kw:
            response = {"code": 401, "message": "token is missing!"}
            return response
        else:
            if kw.get('token', False):
                customer = self.get_customer(kw.get('token'))
                if customer:
                    root_categorys = request.env['product.category'].sudo().search([('parent_id', '=', False)])
                    data = []
                    for root_category in root_categorys:
                        categorys = request.env['product.category'].sudo().search(
                            [('parent_id', '=', root_category.id)])
                        if categorys:
                            data.append(self.category_data(root_category))
                    response = {"code": 200, "message": "All categorys", "data": data}
                    return response
                else:
                    response = {"code": 401, "message": "token is missing!"}
                    return response

    @http.route('/api/get/product', type='json', methods=['POST'], auth='public', sitemap=False)
    def get_product(self, **kw):
        """{
                    "params": {
                        "token":"token",
                        "category":"category.id",
                        "brand":"brand.id"
                    }
                }"""
        if not kw:
            response = {"code": 401, "message": "token is missing!"}
            return response
        else:
            if kw.get('token', False):
                customer = self.get_customer(kw.get('token'))
                if customer:
                    if bool(kw.get('brand', False))!=True or int(kw.get('brand', False)) == 0:
                        products = request.env['product.template'].sudo().search(
                            [('categ_id', '=', int(kw.get('category')))])
                    else:
                        products = request.env['product.template'].sudo().search(
                            [('categ_id', '=', int(kw.get('category'))), ('brand_id', '=', int(kw.get('brand')))])
                    data = []
                    for product in products:
                        data.append(self.product_data(product))
                    response = {"code": 200, "message": "All products", "data": data}
                    return response
                else:
                    response = {"code": 401, "message": "token is missing!"}
                    return response

    @http.route('/api/home/data', type='json', methods=['POST'], auth='public', sitemap=False)
    def home_data(self, **kw):
        """{
                    "params": {
                        "token":"token",
                    }
                }"""
        if not kw:
            response = {"code": 401, "message": "token is missing!"}
            return response
        else:
            if kw.get('token', False):
                customer = self.get_customer(kw.get('token'))
                if customer:
                    response = {"code": 200, "message": "Home Data", "data": {"best_seller": self.best_seller()}}
                    return response
                else:
                    response = {"code": 401, "message": "token is missing!"}
                    return response

    @http.route('/api/add/card', type='json', methods=['POST'], auth='public', sitemap=False)
    def add_card(self, **kw):
        """{
                    "params": {
                        "token":"token",
                        "product":{
                        "id":"id",
                        "quantity":"quantity",
                        "units_of_measure":"uom.id"}
                    }
                }"""
        if not kw:
            response = {"code": 401, "message": "token is missing!"}
            return response
        else:
            if kw.get('token', False):
                customer = self.get_customer(kw.get('token'))
                if customer:
                    sale_order = request.env['sale.order'].sudo().search(
                        [('partner_id', '=', customer.id), ('state', 'in', ['draft', 'sent'])], limit=1)
                    if sale_order:
                        sale_order_line = request.env['sale.order.line'].sudo().search(
                            [('order_id', '=', sale_order.id), ('product_id', '=', int(kw.get('product').get("id")))],
                            limit=1)
                        if sale_order_line:
                            if int(kw.get('product').get("quantity")) == 0:
                                sale_order_line.sudo().unlink()
                                sale_order.sudo().check_cancel()
                            else:
                                sale_order_line.product_uom_qty = int(kw.get('product').get("quantity"))
                                sale_order_line.product_uom = int(kw.get('product').get("units_of_measure"))

                        elif int(kw.get('product').get("quantity")) != 0:
                            sale_order.order_line = [(0, 0,
                                                      {
                                                          "product_id": int(kw.get('product').get("id")) or False,
                                                          "product_uom_qty": int(
                                                              kw.get('product').get("quantity")) or False,
                                                          "product_uom": int(
                                                              kw.get('product').get("units_of_measure")) or False,
                                                      })]
                    elif int(kw.get('product').get("quantity")) != 0:
                        sale_order = request.env['sale.order'].sudo().create({
                            "partner_id": customer.id,
                            "order_line": [(0, 0,
                                            {
                                                "product_id": int(kw.get('product').get("id")) or False,
                                                "product_uom_qty": int(kw.get('product').get("quantity")) or False,
                                                "product_uom": int(
                                                    kw.get('product').get("units_of_measure")) or False,
                                            })]
                        })
                    response = {"code": 200, "message": "Add Card",
                                "data": {"sale_order": {'id': sale_order.id, "name": sale_order.name}}}
                    return response
                else:
                    response = {"code": 401, "message": "token is missing!"}
                    return response

    @http.route('/api/sale/order/details', type='json', methods=['POST'], auth='public', sitemap=False)
    def sale_order_details(self, **kw):
        """{
                    "params": {
                        "token":"token",
                        "sale_oedr_id":"sale_oedr.id"
                    }
                }"""
        if not kw:
            response = {"code": 401, "message": "All data is missing!"}
            return response
        else:
            if kw.get('token', False):
                customer = self.get_customer(kw.get('token'))
                if customer:
                    if kw.get('sale_oedr_id', False):
                        sale_order = request.env['sale.order'].sudo().search(
                            [('id', '=', int(kw.get('sale_oedr_id')))], limit=1)
                    else:
                        sale_order = request.env['sale.order'].sudo().search(
                            [('partner_id', '=', customer.id), ('state', 'in', ['draft', 'sent'])], limit=1)

                    data = {}
                    if sale_order:
                        data = self.sale_order_data(sale_order)
                    response = {"code": 200, "message": "sale order data", "data": data}
                    return response
                else:
                    response = {"code": 401, "message": "token is missing!"}
                    return response

    @http.route('/api/sale/order/confirm', type='json', methods=['POST'], auth='public', sitemap=False)
    def sale_order_confirm(self, **kw):
        """{
                    "params": {
                        "token":"token",
                    }
                }"""
        if not kw:
            response = {"code": 401, "message": "All data is missing!"}
            return response
        else:
            if kw.get('token', False):
                customer = self.get_customer(kw.get('token'))
                if customer:
                    sale_order = request.env['sale.order'].sudo().search(
                            [('partner_id', '=', customer.id), ('state', 'in', ['draft', 'sent'])], limit=1)

                    data = {}
                    if sale_order:
                        sale_order.sudo().action_confirm()
                        data = self.sale_order_data(sale_order)
                    response = {"code": 200, "message": "sale order data", "data": data}
                    return response
                else:
                    response = {"code": 401, "message": "token is missing!"}
                    return response

    @http.route('/api/sale/order/history', type='json', methods=['POST'], auth='public', sitemap=False)
    def order_history(self, **kw):
        """{"params": {
                        "token":"token",
                    }
                }"""
        if not kw:
            response = {"code": 401, "message": "all data is missing!"}
            return response
        else:
            if kw.get('token', False):
                customer = self.get_customer(kw.get('token'))
                if customer:
                    sale_orders = request.env['sale.order'].sudo().search(
                        [('partner_id', '=', customer.id), ('state', 'in', ['sale'])])
                    data = []
                    for sale_order in sale_orders:
                        data.append( self.sale_order_data(sale_order))
                    response = {"code": 200, "message": "order history", "data": data}
                    return response
                else:
                    response = {"code": 401, "message": "token is missing!"}
                    return response

    @http.route('/api/sale/order/reorder', type='json', methods=['POST'], auth='public', sitemap=False)
    def order_reorder(self, **kw):
        """{"params": {
                        "token":"token",
                        "sale_order":"sale_order_id",

                    }
                }"""
        if not kw:
            response = {"code": 401, "message": "all data is missing!"}
            return response
        else:
            if kw.get('token', False):
                customer = self.get_customer(kw.get('token'))
                if customer:
                    sale_order = request.env['sale.order'].sudo().search(
                        [('id', '=', int(kw.get('sale_order')))],limit=1)
                    data = {}
                    if sale_order:
                        order= request.env['sale.order'].sudo().create({
                            "partner_id": sale_order.partner_id.id,
                            "order_line": sale_order.order_line.ids
                        })
                        data=self.sale_order_data(order)
                    response = {"code": 200, "message": "order data", "data": data}
                    return response
                else:
                    response = {"code": 401, "message": "token is missing!"}
                    return response

    # @http.route('/api/customer/verified', type='json', methods=['POST'], auth='public', sitemap=False)
    # def customer_verified(self, **kw):
    #     """{"params": {
    #                     "token":"token",
    #                 }
    #             }"""
    #     if not kw:
    #         response = {"code": 401, "message": "all data is missing!"}
    #         return response
    #     else:
    #         if kw.get('token', False):
    #             customer = self.get_customer(kw.get('token'))
    #             data={"is_verified":customer.is_verified}
    #             if customer:
    #                 response = {"code": 200, "data": data}
    #                 return response
    #             else:
    #                 response = {"code": 401, "message": "token is missing!"}
    #                 return response
