# -*- coding: utf-8 -*-

{
    'name': 'ICS Pret Accounting',
    'version': '13.0.1.0.0',
    'summary': 'ICS Pret Accounting',
    'description': """
        Create accounting entries for Loan requests.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Infotech Consulting Services",
    'company': 'Infotech Consulting Services',
    'maintainer': 'Infotech Consulting Services',
    'website': "http://www.ics-tunisie.com",
    'depends': [
        'base', 'hr_payroll_community', 'hr', 'account', 'ics_pret',
    ],
    'data': [
        'views/hr_pret_config.xml',
        'views/hr_pret_acc.xml',
        'views/rules.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
