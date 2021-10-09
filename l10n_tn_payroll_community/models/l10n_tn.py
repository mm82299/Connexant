# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.base.models import decimal_precision as dp


class Hr_Contract(models.Model):
    _inherit = 'hr.contract'

    nationalite = fields.Char(string="Nationalitie", required=False, )
    qualif = fields.Char(string="Qualification", required=False, )
    niveau = fields.Char(string="Niveau", required=False, )
    coef = fields.Char(string="Coefficient", required=False, )


class ResCompany(models.Model):
    _inherit = 'res.company'

    plafond_secu = fields.Float(string="Plafond de la Securite Sociale", digits_compute=dp.get_precision('Payroll'))
    nombre_employes = fields.Integer(string="Nombre d\'employes'", required=False, )
    cotisation_prevoyance = fields.Float(string="Cotisation Patronale Prevoyance",
                                         digits_compute=dp.get_precision('Payroll'))
    org_ss = fields.Char(string="Organisme de securite sociale", )
    conv_coll = fields.Char(string="Convention collective", required=False, )


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    payment_mode = fields.Char('Mode de paiement')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    matricule_cnss = fields.Integer(string="Matricule CNSS", required=False)
    num_chezemployeur = fields.Integer(string="Numero chez l\'employeur", required=False)

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    matricule_cnss = fields.Integer(string="Matricule CNSS", required=False, relate="employee_id.matricule_cnss")
    num_chezemployeur = fields.Integer(string="Numero chez l\'employeur", required=False, relate="employee_id.num_chezemployeur")
