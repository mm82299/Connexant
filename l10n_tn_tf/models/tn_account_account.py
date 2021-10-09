from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    tn_enable_tax = fields.Boolean(string="Activer droit de timbre")
    tn_sales_tax_account = fields.Many2one('account.account', string="Compte droit de timbre vente")
    tn_purchase_tax_account = fields.Many2one('account.account', string="Compte droit de timbre achat")


class TnResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tn_enable_tax = fields.Boolean(string="Activer droit de timbre", related='company_id.tn_enable_tax', readonly=False)
    tn_sales_tax_account = fields.Many2one('account.account', string="Compte droit de timbre vente", related='company_id.tn_sales_tax_account', readonly=False)
    tn_purchase_tax_account = fields.Many2one('account.account', string="Compte droit de timbre achat", related='company_id.tn_purchase_tax_account', readonly=False)
