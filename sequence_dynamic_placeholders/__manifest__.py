# -*- coding: utf-8 -*-
{
    'name': 'Sequence Dynamic Placeholders',
    'version': '16.0.1.0.0',
    'summary': 'Replace placeholders in sequences with dynamic values',
    'description': """
        This module allows configuring dynamic placeholders in sequences.
        You can define placeholders for month and year that will be replaced
        with custom characters or values based on mapping configurations.

        Features:
        - Month and year placeholders
        - Optional per sequence
    """,
    'category': 'Technical',
    'author': 'Kıta',
    'website': 'kitayazilim.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_sequence_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
