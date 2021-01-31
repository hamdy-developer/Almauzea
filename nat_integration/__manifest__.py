# -*- coding: utf-8 -*-


{
    'name': 'nat_integration',
    'version': '1.2',
    'category': 'lenght_width',
    'depends': ['base', 'product', 'stock', 'product_brand_inventory', 'sale','sale_management', 'almuazae_purchase'],
    'data': [
        "security/ir.model.access.csv",
        "views/view.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
