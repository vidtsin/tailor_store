{
    'name': 'Crystal Reporting',
    'version': '1.0',
    'sequence': 1,
    'author': "Allion Technologies PVT Ltd",
    'website': 'http://www.alliontechnologies.com/',
    'summary': 'Crystal Reporting',
    'description': """Helps to create crystal reports""",
    'depends': [
        'hr',
    ],
    'data': [
            'security/ir.model.access.csv',
            'data/mail_templates.xml',
            'reports/crystal_report.xml',
            'views/icon.xml',
            'views/report_types_view.xml',
            'views/crystal_reporting_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}