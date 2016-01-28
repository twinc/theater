# -*- coding: utf-8 -*-
{
    'name': "Theater",

    'summary': """Manage seats of theater""",

    'description': """
        Manage Theater:
            - Select Movie
            - Select Time
            - attendees registration
    """,

    'author': "Twin C.",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/theater.xml',
        'views/partner.xml',
        'reports.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}