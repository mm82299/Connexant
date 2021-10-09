# -*- coding: utf-8 -*-
{
    'name': "Tunisian TF",
    'description': """
        Add Fiscal Timber Tunisian Tax. 
    """,
    'author': "Infotech Consulting Services - ICS",
    'website': "http://www.ics-tunisie.com",
    'category': 'Accounting',
    'version': '13.0.0.1',
    'depends': ['l10n_tn', 'sale'],
    'data': [
        'views/fiscal_position.xml',
        'data/fiscal_position.xml',
        'views/report_invoicel.xml',
        'views/report_quote.xml',
        'views/tn_account_account.xml',
        'views/tn_account_invoice_supplier_form.xml',
        'views/assets.xml',
    ],
}
