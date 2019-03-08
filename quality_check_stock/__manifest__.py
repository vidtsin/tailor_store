{
    'name': 'Quality Check',
    'version': '1.0',
    'category': 'Warehouse',
    'sequence': 1,
    'author': "Allion Technologies PVT Ltd",
    'website': 'http://www.alliontechnologies.com/',
    'summary': 'Manage internal quality check process',
    'description': """This module contains quality control process of the Tailor Store Pvt Ltd. Transfer the real stock after the qulity check process to the real stock invetory""",
    'depends': ['stock'],
    'data': [
        'security/security_qc_process.xml',
        'views/stock_picking_views_inherit.xml',
        'views/operation_types_inherit.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}