# -*- coding: utf-8 -*-

{
    'name': 'Open ICS Advance Salary',
    'version': '13.0.1.0.1',
    'summary': 'Advance Salary In HR',
    'description': """
        Helps you to manage Advance Salary Request of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Infotech Consulting Services",
    'company': 'Infotech Consulting Services',
    'maintainer': 'Infotech Consulting Services',
    'website': "http://www.ics-tunisie.com",
    'depends': [
        'hr_payroll_community', 'hr', 'account', 'hr_contract', 'ics_pret',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/salary_structure.xml',
        'views/salary_advance.xml',
        'views/rules.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

