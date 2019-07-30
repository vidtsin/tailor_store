{
    'name': 'Global Leaves',
    'version': '1.0',
    'sequence': 1,
    'author': "Allion Technologies PVT Ltd",
    'website': 'http://www.alliontechnologies.com/',
    'summary': 'Global Leaves',
    'description': """This module contains Global Leaves process functionality""",
    'depends': [
        'base',
        'hr',
        'hr_holidays',
    ],
    'data': [
        'views/resource_leaves_inherit_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}