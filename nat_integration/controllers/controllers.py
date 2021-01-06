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
        print('data',kw)
        if not kw:
            response = {"result": {"code": 401, "message": "All required data are missing!"}}
            return response
        if kw.get('mobile_number',False):
            custome = request.env['res.partner'].sudo().search([('mobile', '=', kw.get('mobile_number','False'))],limit=1)

            if custome:
                response = {"result": {"code": 200, "message": "Custome already exist",}}
                return response
            else:
                response = {"result": {"code": 404, "message": "Custome Not Exist"}}
            return response

