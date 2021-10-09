# -*- coding: utf-8 -*-
from odoo import models, api, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pret_id = fields.Many2one('hr.pret', 'Identifiant du prêt')
