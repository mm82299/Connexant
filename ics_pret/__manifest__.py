# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Anusha P P (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': 'Gestion des prêts',
    'version': '13.0.1.1.0',
    'summary': 'Gérer les demandes de prêt',
    'description': """
       Vous aide à gérer les demandes de prêt du personnel de votre entreprise.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Infotech Consulting Services - ICS",
    'company': 'Infotech Consulting Services - ICS',
    'maintainer': 'Infotech Consulting Services',
    'website': "http://www.ics-tunisie.com",
    'depends': [
        'base', 'hr_payroll_community', 'hr', 'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_pret_seq.xml',
        'data/salary_rule_pret.xml',
        'views/hr_pret.xml',
        'views/hr_payroll.xml',
        'views/rules.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
