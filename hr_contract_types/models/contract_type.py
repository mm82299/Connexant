# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ContractType(models.Model):
    _name = 'hr.contract.type'
    _description = 'Contract Type'
    _order = 'sequence, id'

    name = fields.Char(string='Contract Type', required=True, help="Name")
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)
    active = fields.Boolean(default=True)
    term_ids = fields.One2many('hr.contract.type.term', 'contract_type_id')


class HrContractTypeTerm(models.Model):
    _name = 'hr.contract.type.term'
    _description = 'Employee Contract Types Terms'

    contract_type_id = fields.Many2one('hr.contract.type')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    body = fields.Text(required=True)


class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    type_id = fields.Many2one('hr.contract.type', string="Employee Category",
                              required=True, help="Employee category",
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))
