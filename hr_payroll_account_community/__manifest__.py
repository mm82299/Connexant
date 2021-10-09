# -*- coding: utf-8 -*-

{
    'name': 'Odoo13 Payroll Accounting',
    'category': 'Generic Modules/Human Resources',
    'summary': """
          Generic Payroll system Integrated with Accounting,Expense Encoding,Payment Encoding,Company Contribution Management
    """,
    'description': """Odoo13 Payroll Accounting""",
    'version': '13.0.1.',
    'author': 'Infotech Consulting Services',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Infotech Consulting Services',
    'website': 'http://www.ics-tunisie.com',
    'depends': ['hr_payroll_community', 'account'],
    'data': ['views/hr_payroll_account_views.xml'],
    'test': ['../account/test/account_minimal_test.xml'],
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
}