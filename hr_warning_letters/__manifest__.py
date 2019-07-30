{
    'name': 'HR Warning Letters',
    'version': '1.0',
    'sequence': 1,
    'author': "Allion Technologies PVT Ltd",
    'website': 'http://www.alliontechnologies.com/',
    'summary': 'HR Warning Letters',
    'description': """Helps the HR to issue warning letters""",
    'depends': [
        'hr',
        'crystal_reporting',
    ],
    'data': [
            'security/ir.model.access.csv',
            'data/mail_templates.xml',
            'reports/crystal_report.xml',
            'views/icon.xml',
            'views/hr_warning_letters_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}