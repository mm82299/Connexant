# -*- coding: utf-8 -*-
{
    'name': "l10n_tn_payroll_community",
    'summary': """
        Tunisian Payroll Rules.""",
    'description': """
        Tunisian Payroll Rules.
    """,
    'author': "Infotech Consulting Services - ICS ",
    'website': "http://www.ics-tunisie.com",
    'category': 'Payroll Localization',
    'version': '0.1',
    'depends': ['hr_payroll_community', 'l10n_tn'],
    'data': [
        'security/ir.model.access.csv',
        'views/l10n_tn_payroll_view.xml',
        'views/res_config_settings_views.xml',
        'data/l10n_tn_payroll_data.xml',
        "report/l10n_tn_hr_payroll_report.xml",
        "report/report_l10n_tn_fiche_paye.xml"
    ],
    "installable": True,
    "application": False,
}
