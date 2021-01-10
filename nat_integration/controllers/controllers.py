# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import requests
import base64
import json
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

HEADERS = {'Content-Type': 'application/json'}


class NatApi(http.Controller):

    def gey_customer(self, token):
        customer = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
        return customer

    @http.route('/api/check/customer', type='json', methods=['POST'], auth='public', sitemap=False)
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
                    response = {"code": 200, "message": "Custome already exist","data":True }
                    return response
                else:
                    response = {"code": 200, "message": "Custome Not Exist","data":False}
                return response

    @http.route('/api/get/erea', type='json', methods=['GET'], auth='public', sitemap=False)
    def get_erea(self, **kw):
        data = []
        ereas = request.env['area.area'].sudo().search([])
        for erea in ereas:
            data.append({'id': erea.id, 'name': erea.name})
        response = {"code": 200,  "message": "All areas","data": data}
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
            response =  {"code": 401, "message": "All required data are missing!"}
            return response
        else:
            if kw.get('name', False) and kw.get('password', False):
                vals = {
                    'is_company': False,
                    'customer_rank': 1,
                    'type': 'private',
                    'name': kw.get('name'),
                    'shop_name': kw.get('shop_name'),
                    'email': kw.get('email'),
                    'phone': kw.get('mobile'),
                    'area_id': int(kw.get('area')),
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
                response =  {"code": 200, "message": "create new customer" ,"data": valus}
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
            if kw.get('name', False) and kw.get('password', False) and kw.get('token', False):
                vals = {
                    'is_company': False,
                    'customer_rank': 1,
                    'type': 'private',
                    'name': kw.get('name'),
                    'shop_name': kw.get('shop_name'),
                    'email': kw.get('email'),
                    'phone': kw.get('mobile'),
                    'area_id': int(kw.get('area')),
                    'zip': kw.get('zip'),
                    'street': kw.get('street'),
                    'street2': kw.get('street2'),
                    'password': kw.get('password'),
                }
                customer = self.gey_customer(kw.get('token'))
                if customer:
                    customer.sudo().write(vals)
                    response = {"code": 200, "message": "Edit customer data","data":kw}
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
                customer = self.gey_customer(kw.get('token'))
                if customer:
                    customer.sudo().unlink()
                    response = {"code": 200, "message": "Customer deleted","data":{}}
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
                area_data = {}
                if customer.area_id:
                    area_data = {'id': customer.area_id.id, 'name': customer.area_id.name}
                if customer:
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
                    response = {"code": 200,  "message": "login","data": valus}
                    return response
                else:
                    response = {"code": 401, "message": "Customer Not Exist"}
                    return response
            else:
                response = {"code": 401, "message": "mobile or password is missing!"}
                return response

    @http.route('/api/get/product', type='json', methods=['POST'], auth='public', sitemap=False)
    def get_product(self, **kw):
        """{
            "params": {
                "token": "token",
            }
        }"""
        data = []
        products = request.env['product.product'].sudo().search([])
        for product in products:
            data.append(
                {'id': product.id, 'name': product.name, 'sale_price': product.lst_price, 'picture': product.image_1920,
                 'category': {'id': product.categ_id.id,'name':product.categ_id.name},'barcode':product.barcode,})
        response ={"code": 200, "products": data}
        return response

    # @http.route('/api/get/category', type='json', methods=['GET'], auth='public', sitemap=False)
    # def get_category(self, **kw):
    #     data=[]
    #     categorys = request.env['product.category'].sudo().search([])
    #     for category in categorys:
    #         data.append({'id':category.id,'name':category.name})
    #     response = {"result": {"code": 200, "data":data }}
    #     return response
