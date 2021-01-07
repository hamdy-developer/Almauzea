# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import requests
import base64
import json
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

HEADERS = {'Content-Type': 'application/json'}


class NatApi(http.Controller):

    @http.route('/api/check/customer', type='json', methods=['POST'], auth='public', sitemap=False)
    def check_customer(self, **kw):
        """{
            "params": {
                "mobile_number": "0100"
            }
        }"""
        if not kw:
            response = {"result": {"code": 401, "message": "All required data are missing!"}}
            return response
        else:
            if kw.get('mobile_number', False):
                custome = request.env['res.partner'].sudo().search([('phone', '=', kw.get('mobile_number', 'False'))],
                                                                   limit=1)

                if custome:
                    response = {"result": {"code": 200, "message": "Custome already exist", }}
                    return response
                else:
                    response = {"result": {"code": 404, "message": "Custome Not Exist"}}
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
                        "city": "city",
                        "zip": "zip",
                        "street": "street",
                        "street2": "street2"
                    }
                }"""
        if not kw:
            response = {"result": {"code": 401, "message": "All required data are missing!"}}
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
                    'city': kw.get('city'),
                    'zip': kw.get('zip'),
                    'street': kw.get('street'),
                    'street2': kw.get('street2'),
                    'password': kw.get('password'),
                }
                new_customer = request.env['res.partner'].sudo().create(vals)
                new_customer.sudo().generate_token()
                response = {"result": {"code": 200, "token": new_customer.token}}
                return response
            else:
                response = {"result": {"code": 401, "message": "password or name is missing!"}}
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
                        "city": "city",
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
                    'city': kw.get('city'),
                    'zip': kw.get('zip'),
                    'street': kw.get('street'),
                    'street2': kw.get('street2'),
                    'password': kw.get('password'),
                }
                customer = request.env['res.partner'].sudo().search([('token', '=', kw.get('token'))], limit=1)
                if customer:
                    customer.sudo().write(vals)
                    response = {"result": {"code": 200, "Edit": "done"}}
                    return response
                else:
                    response = {"result": {"code": 401, "token": "missing"}}
                    return response
            else:
                response = {"result": {"code": 401, "message": "password or name or token is missing!"}}
                return response

    @http.route('/api/delete/customer', type='json', methods=['POST'], auth='public', sitemap=False)
    def delete_customer(self, **kw):
        """{
                    "params": {
                        "token":"token",
                    }
                }"""
        if not kw:
            response = {"result": {"code": 401, "message": "All required data are missing!"}}
            return response
        else:
            if kw.get('token', False):
                customer = request.env['res.partner'].sudo().search([('token', '=', kw.get('token'))], limit=1)
                if customer:
                    customer.sudo().unlink()
                    response = {"result": {"code": 200, "delete": "done"}}
                    return response
                else:
                    response = {"result": {"code": 401, "token": "Not Exist"}}
                    return response
            else:
                response = {"result": {"code": 401, "message": "token is missing!"}}
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
            response = {"result": {"code": 401, "message": "All required data are missing!"}}
            return response
        else:
            if kw.get('mobile', False) and kw.get('password', False):
                customer = request.env['res.partner'].sudo().search([('password', '=', kw.get('password')),('phone', '=', kw.get('mobile'))], limit=1)
                if customer:
                    valus = {
                        "token":  customer.token,
                        "password": customer.password,
                        "name": customer.name,
                        "shop_name": customer.shop_name,
                        "email": customer.email,
                        "mobile": customer.phone,
                        "city": customer.city,
                        "zip": customer.zip,
                        "street": customer.street,
                        "street2": customer.street2
                    }
                    response = {"result": {"code": 200, "delete": valus}}
                    return response
                else:
                    response = {"result": {"code": 401, "message": "Customer Not Exist"}}
                    return response
            else:
                response = {"result": {"code": 401, "message": "mobile or password is missing!"}}
                return response
