{
    'name': 'HR Leave Inherit',
    'version': '1.0',
    'sequence': 1,
    'author': "Allion Technologies PVT Ltd",
    'website': 'http://www.alliontechnologies.com/',
    'summary': 'HR Leave Inherit',
    'description': """Brings third Validation to Approve leave""",
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_holidays_inherit_view.xml',
        'security/security_groups.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}