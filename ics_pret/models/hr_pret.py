# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class HrPret(models.Model):
    _name = 'hr.pret'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Pret Request"

    @api.model
    def default_get(self, field_list):
        result = super(HrPret, self).default_get(field_list)
        if result.get('user_id'):
            ts_user_id = result['user_id']
        else:
            ts_user_id = self.env.context.get('user_id', self.env.user.id)
        result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
        return result

    def _compute_pret_amount(self):
        total_paid = 0.0
        for pret in self:
            for line in pret.pret_lines:
                if line.paid:
                    total_paid += line.amount
            balance_amount = pret.pret_amount - total_paid
            pret.total_amount = pret.pret_amount
            pret.balance_amount = balance_amount
            pret.total_paid_amount = total_paid

    name = fields.Char(string="Nom du prêt", default="Pret/", readonly=True, help="Name of the pret")
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True, help="Date")
    employee_id = fields.Many2one('hr.employee', string="Employé(e)", required=True, help="Employee", default=lambda self: self.env.user.employee_id.id)
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,
                                    string="Département", help="Employee")
    installment = fields.Integer(string="No de Versements", default=1, help="Number of installments")
    payment_date = fields.Date(string="Date de Début du Paiement", required=True, default=fields.Date.today(), help="Date of "
                                                                                                             "the "
                                                                                                             "paymemt")
    pret_lines = fields.One2many('hr.pret.line', 'pret_id', string="Ligne de prêt", index=True)
    company_id = fields.Many2one('res.company', 'Compagnie', readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Devise', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Poste",
                                   help="Job position")
    pret_amount = fields.Float(string="Montant du prêt", required=True, help="pret amount")
    total_amount = fields.Float(string="Montant total", store=True, readonly=True, compute='_compute_pret_amount',
                                help="Total pret amount")
    balance_amount = fields.Float(string="Montant du solde", store=True, compute='_compute_pret_amount', help="Balance amount")
    total_paid_amount = fields.Float(string="Montant total payé", store=True, compute='_compute_pret_amount',
                                     help="Total paid amount")

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('waiting_approval_1', 'Soumise'),
        ('approve', 'Approuvée'),
        ('refuse', 'Refusé'),
        ('cancel', 'Annulé'),
    ], string="État", default='draft', track_visibility='onchange', copy=False, )

    @api.model
    def create(self, values):
        pret_count = self.env['hr.pret'].search_count(
            [('employee_id', '=', self.env.user.employee_id.id), ('state', '=', 'approve'),
             ('balance_amount', '!=', 0)])
        if pret_count:
            raise ValidationError(_("L'employé a déjà un versement en attente"))
        else:
            values['name'] = self.env['ir.sequence'].get('hr.pret.seq') or ' '
            res = super(HrPret, self).create(values)
            return res

    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for pret in self:
            pret.pret_lines.unlink()
            date_start = datetime.strptime(str(pret.payment_date), '%Y-%m-%d')
            amount = pret.pret_amount / pret.installment
            for i in range(1, pret.installment + 1):
                self.env['hr.pret.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': pret.employee_id.id,
                    'pret_id': pret.id})
                date_start = date_start + relativedelta(months=1)
            pret._compute_pret_amount()
        return True

    def action_refuse(self):
        return self.write({'state': 'refuse'})

    def action_submit(self):
        self.write({'state': 'waiting_approval_1'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_approve(self):
        for data in self:
            if not data.pret_lines:
                raise ValidationError(_("Veuillez calculer le versement"))
            else:
                self.write({'state': 'approve'})

    def unlink(self):
        for pret in self:
            if pret.state not in ('draft', 'cancel'):
                raise UserError(
                    "Vous ne pouvez pas supprimer un prêt qui n'est pas à l'état brouillon ou annulé")
        return super(HrPret, self).unlink()


class InstallmentLine(models.Model):
    _name = "hr.pret.line"
    _description = "Installment Line"

    date = fields.Date(string="Date du Paiement", required=True, help="Date du Paiement")
    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employé(e)")
    amount = fields.Float(string="Montant", required=True, help="Amount")
    paid = fields.Boolean(string="Payé", help="Paid")
    pret_id = fields.Many2one('hr.pret', string="Prêt Réf.", help="pret")
    payslip_id = fields.Many2one('hr.payslip', string="Fiche de paie Réf.", help="Payslip")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_prets(self):
        """This compute the pret amount and total prets count of an employee.
            """
        self.pret_count = self.env['hr.pret'].search_count([('employee_id', '=', self.id)])

    pret_count = fields.Integer(string="Nombre de prêts", compute='_compute_employee_prets')
