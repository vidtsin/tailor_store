{
    'name': "Stock Ageing Analysis",
    'version': '1.0',
    'summary': """Product Ageing Analysis With Filtration""",
    'description': "With this module, we can perform stock ageing analysis with optional filters suchas location, category, etc.",
    'author': "Allion Technologies PVT Ltd",
    'website': 'http://www.alliontechnologies.com/',
    'category': 'Warehouse',
    'depends': ['product', 'stock'],
    'data': [
        'reports/report_ageing_products.xml',
        'security/product_ageing_security.xml',
        'security/ir.model.access.csv',
        'views/product_ageing.xml'
    ],
    'license': 'GPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}