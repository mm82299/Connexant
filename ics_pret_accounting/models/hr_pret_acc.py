# -*- coding: utf-8 -*-
import time
from odoo import models, api, fields
from odoo.exceptions import UserError


class HrPretAcc(models.Model):
    _inherit = 'hr.pret'

    employee_account_id = fields.Many2one('account.account', string="Compte de Prêt")
    treasury_account_id = fields.Many2one('account.account', string="Compte de Trésorerie")
    journal_id = fields.Many2one('account.journal', string="Journal")

    state = fields.Selection([
        ('draft', 'Brouillan'),
        ('waiting_approval_1', 'Soumise'),
        ('waiting_approval_2', "En attente d'approbation"),
        ('approve', 'Approuvée'),
        ('refuse', 'Refusé'),
        ('cancel', 'Annulé'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )

    def action_approve(self):
        """This create account move for request.
            """
        pret_approve = self.env['ir.config_parameter'].sudo().get_param('account.pret_approve')
        contract_obj = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
        if not contract_obj:
            raise UserError('You must Define a contract for employee')
        if not self.pret_lines:
            raise UserError('You must compute installment before Approved')
        if pret_approve:
            self.write({'state': 'waiting_approval_2'})
        else:
            if not self.employee_account_id or not self.treasury_account_id or not self.journal_id:
                raise UserError("You must enter employee account & Treasury account and journal to approve ")
            if not self.pret_lines:
                raise UserError('You must compute pret Request before Approved')
            timenow = time.strftime('%Y-%m-%d')
            for pret in self:
                amount = pret.pret_amount
                pret_name = pret.employee_id.name
                reference = pret.name
                journal_id = pret.journal_id.id
                debit_account_id = pret.treasury_account_id.id
                credit_account_id = pret.employee_account_id.id
                debit_vals = {
                    'name': pret_name,
                    'account_id': debit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    'pret_id': pret.id,
                }
                credit_vals = {
                    'name': pret_name,
                    'account_id': credit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    'pret_id': pret.id,
                }
                vals = {
                    'narration': pret_name,
                    'ref': reference,
                    'journal_id': journal_id,
                    'date': timenow,
                    'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
                }
                move = self.env['account.move'].create(vals)
                move.post()
            self.write({'state': 'approve'})
        return True

    def action_double_approve(self):
        """This create account move for request in case of double approval.
            """
        if not self.employee_account_id or not self.treasury_account_id or not self.journal_id:
            raise UserError("You must enter employee account & Treasury account and journal to approve ")
        if not self.pret_lines:
            raise UserError('You must compute pret Request before Approved')
        timenow = time.strftime('%Y-%m-%d')
        for pret in self:
            amount = pret.pret_amount
            pret_name = pret.employee_id.name
            reference = pret.name
            journal_id = pret.journal_id.id
            debit_account_id = pret.treasury_account_id.id
            credit_account_id = pret.employee_account_id.id
            debit_vals = {
                'name': pret_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
                'pret_id': pret.id,
            }
            credit_vals = {
                'name': pret_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
                'pret_id': pret.id,
            }
            vals = {
                'narration': pret_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.post()
        self.write({'state': 'approve'})
        return True


class HrpretLineAcc(models.Model):
    _inherit = "hr.pret.line"

    def action_paid_amount(self):
        """This create the account move line for payment of each installment.
            """
        timenow = time.strftime('%Y-%m-%d')
        for line in self:
            if line.pret_id.state != 'approve':
                raise UserError("pret Request must be approved")
            amount = line.amount
            pret_name = line.employee_id.name
            reference = line.pret_id.name
            journal_id = line.pret_id.journal_id.id
            debit_account_id = line.pret_id.employee_account_id.id
            credit_account_id = line.pret_id.treasury_account_id.id
            debit_vals = {
                'name': pret_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
            }
            credit_vals = {
                'name': pret_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
            }
            vals = {
                'narration': pret_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.post()
        return True


class HrPayslipAcc(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.pret_line_id:
                line.pret_line_id.action_paid_amount()
        return super(HrPayslipAcc, self).action_payslip_done()
