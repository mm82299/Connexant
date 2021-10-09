# -*- coding: utf-8 -*-

{
    'name': 'Odoo13 Employee Contracts Types',
    'version': '13.0.1',
    'category': 'Generic Modules/Human Resources',
    'summary': """
        Contract type in contracts
    """,
    'description': """Odoo13 Employee Contracts Types""",
    'author': 'Infotech Consulting Services',
    'company': 'Infotech Consulting Services',
    'maintainer': 'Infotech Consulting Services',
    'website': 'http://www.ics-tunisie.com',
    'depends': ['hr', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/contract_view.xml',
        'data/hr_contract_type_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}