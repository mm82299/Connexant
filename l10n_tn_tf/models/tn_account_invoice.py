from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class TnGlobalTaxInvoice(models.Model):
    _inherit = "account.move"

    tn_amount_global_tax = fields.Monetary(string="Droit de Timbre", readonly=True, compute='_compute_amount',
                                           track_visibility='always', store=True)
    tn_enable_tax = fields.Boolean(compute='tn_verify_tax')
    tn_sales_tax_account_id = fields.Integer(compute='tn_verify_tax')
    tn_purchase_tax_account_id = fields.Integer(compute='tn_verify_tax')

    @api.depends('company_id.tn_enable_tax', 'fiscal_position_id')
    def tn_verify_tax(self):
        for rec in self:
            rec.tn_enable_tax = rec.company_id.tn_enable_tax
            tax = rec.fiscal_position_id.stamp_tax_id
            tax2 = rec.fiscal_position_id.stamp_tax_id2
            tax_repartition_lines = tax.invoice_repartition_line_ids.filtered(
                lambda x: x.repartition_type == 'tax') if tax else None
            tax_repartition_lines2 = tax2.invoice_repartition_line_ids.filtered(
                lambda x: x.repartition_type == 'tax') if tax2 else None

            tax_account_id = tax_repartition_lines.account_id.id if tax_repartition_lines else None
            tax_account_id2 = tax_repartition_lines2.account_id.id if tax_repartition_lines2 else None

            rec.tn_sales_tax_account_id = tax_account_id
            rec.tn_purchase_tax_account_id = tax_account_id2

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'fiscal_position_id',
        'partner_id')
    def _compute_amount(self):
        super(TnGlobalTaxInvoice, self)._compute_amount()
        for rec in self:
            # if rec.fiscal_position_id and rec.currency_id.name == 'TND' and rec.tn_enable_tax:
            if rec.fiscal_position_id and rec.tn_enable_tax:
                if 'tn_amount_discount' in rec:
                    rec.tn_calculate_discount()

                rec.tn_calculate_tax()
                rec.tn_update_tunisia_tax()

    def tn_calculate_tax(self):
        for rec in self:
            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            tax = rec.fiscal_position_id.stamp_tax_id
            tax2 = rec.fiscal_position_id.stamp_tax_id2
            # valeur du timbre basée sur celui de vente (tax) et non celui de l'achat (tax2)
            # a developper si besoin d'avoir deux valeurs de timbre!
            if tax.amount != 0.0 and rec.type in type_list:
                rec.tn_amount_global_tax = tax.amount
            else:
                rec.tn_amount_global_tax = 0.0
            if rec.currency_id.name != 'TND':
                rec.tn_amount_global_tax = 0.0
            rec.amount_total = rec.tn_amount_global_tax + rec.amount_total

    def tn_update_tunisia_tax(self):
        for rec in self:
            already_exists = rec.line_ids.filtered(
                lambda line: line.name and line.name.find('Tunisia Tax') == 0)
            terms_lines = rec.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            other_lines = rec.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
            if already_exists:
                amount = rec.tn_amount_global_tax
                if rec.tn_sales_tax_account_id \
                        and (rec.type == "out_invoice"
                             or rec.type == "out_refund") \
                        and rec.fiscal_position_id.stamp_tax_id.amount > 0:
                    if rec.type == "out_invoice":
                        already_exists.update({
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        })
                    else:
                        already_exists.update({
                            'debit': amount > 0.0 and amount or 0.0,
                            'credit': amount < 0.0 and -amount or 0.0,
                        })
                if rec.tn_purchase_tax_account_id \
                        and (rec.type == "in_invoice"
                             or rec.type == "in_refund") \
                        and rec.fiscal_position_id.stamp_tax_id2.amount > 0:
                    if rec.type == "in_invoice":
                        already_exists.update({
                            'debit': amount > 0.0 and amount or 0.0,
                            'credit': amount < 0.0 and -amount or 0.0,
                        })
                    else:
                        already_exists.update({
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        })
                total_balance = sum(other_lines.mapped('balance'))
                total_amount_currency = sum(other_lines.mapped('amount_currency'))
                terms_lines.update({
                    'amount_currency': -total_amount_currency,
                    'debit': total_balance < 0.0 and -total_balance or 0.0,
                    'credit': total_balance > 0.0 and total_balance or 0.0,
                })
            if not already_exists and rec.fiscal_position_id.stamp_tax_id.amount > 0:
                in_draft_mode = rec != rec._origin
                rec.tn_amount_global_tax = 0.0
                if not in_draft_mode:
                    rec._recompute_tunisia_tax_lines()

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        tn_res = super(TnGlobalTaxInvoice, self)._prepare_refund(invoice, date_invoice=None, date=None,
                                                                 description=None, journal_id=None)
        tn_res['tn_amount_global_tax'] = self.tn_amount_global_tax
        return tn_res

    @api.onchange('fiscal_position_id', 'line_ids', 'invoice_line_ids', 'partner_id')
    def _recompute_tunisia_tax_lines(self):
        for rec in self:
            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if rec.fiscal_position_id.stamp_tax_id.amount > 0 and rec.type in type_list:
                if rec.is_invoice(include_receipts=True):
                    in_draft_mode = rec != rec._origin
                    tn_name = "Tunisia Tax"
                    tn_name = tn_name + \
                              " @" + str(rec.fiscal_position_id.stamp_tax_id.tax_group_id.name)
                    terms_lines = rec.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                    already_exists = rec.line_ids.filtered(
                        lambda line: line.name and line.name.find('Tunisia Tax') == 0)
                    if already_exists:
                        amount = rec.tn_amount_global_tax
                        if rec.tn_sales_tax_account_id \
                                and (rec.type == "out_invoice"
                                     or rec.type == "out_refund"):
                            already_exists.update({
                                'name': tn_name,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                            })
                        if rec.tn_purchase_tax_account_id \
                                and (rec.type == "in_invoice"
                                     or rec.type == "in_refund"):
                            already_exists.update({
                                'name': tn_name,
                                'debit': amount > 0.0 and amount or 0.0,
                                'credit': amount < 0.0 and -amount or 0.0,
                            })
                    else:
                        new_tax_line = rec.env['account.move.line']
                        create_method = in_draft_mode and new_tax_line.new or new_tax_line.create

                        if rec.tn_sales_tax_account_id \
                                and (rec.type == "out_invoice"
                                     or rec.type == "out_refund"):
                            amount = rec.tn_amount_global_tax
                            dict = {
                                'move_name': rec.name,
                                'name': tn_name,
                                'price_unit': rec.tn_amount_global_tax,
                                'quantity': 1,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                                'account_id': rec.tn_sales_tax_account_id,
                                'move_id': rec._origin,
                                'date': rec.date,
                                'exclude_from_invoice_tab': True,
                                'partner_id': terms_lines.partner_id.id,
                                'company_id': terms_lines.company_id.id,
                                'company_currency_id': terms_lines.company_currency_id.id,
                            }
                            if rec.type == "out_invoice":
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            if in_draft_mode:
                                rec.line_ids += create_method(dict)
                                # Updation of Invoice Line Id
                                duplicate_id = rec.invoice_line_ids.filtered(
                                    lambda line: line.name and line.name.find('Tunisia Tax') == 0)
                                rec.invoice_line_ids = rec.invoice_line_ids - duplicate_id
                            else:
                                dict.update({
                                    'price_unit': 0.0,
                                    'debit': 0.0,
                                    'credit': 0.0,
                                })
                                rec.line_ids = [(0, 0, dict)]

                        if rec.tn_purchase_tax_account_id \
                                and (rec.type == "in_invoice"
                                     or rec.type == "in_refund"):
                            amount = rec.tn_amount_global_tax
                            dict = {
                                'move_name': rec.name,
                                'name': tn_name,
                                'price_unit': rec.tn_amount_global_tax,
                                'quantity': 1,
                                'debit': amount > 0.0 and amount or 0.0,
                                'credit': amount < 0.0 and -amount or 0.0,
                                'account_id': rec.tn_purchase_tax_account_id,
                                'move_id': rec.id,
                                'date': rec.date,
                                'exclude_from_invoice_tab': True,
                                'partner_id': terms_lines.partner_id.id,
                                'company_id': terms_lines.company_id.id,
                                'company_currency_id': terms_lines.company_currency_id.id,
                            }

                            if rec.type == "in_invoice":
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            rec.line_ids += create_method(dict)
                            # updation of invoice line id
                            duplicate_id = rec.invoice_line_ids.filtered(
                                lambda line: line.name and line.name.find('Tunisia Tax') == 0)
                            rec.invoice_line_ids = rec.invoice_line_ids - duplicate_id

                    if in_draft_mode:
                        # Update the payement account amount
                        terms_lines = rec.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                        other_lines = rec.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                        total_balance = sum(other_lines.mapped('balance'))
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        terms_lines.update({
                            'amount_currency': -total_amount_currency,
                            'debit': total_balance < 0.0 and -total_balance or 0.0,
                            'credit': total_balance > 0.0 and total_balance or 0.0,
                        })
                    else:
                        terms_lines = rec.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                        other_lines = rec.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                        already_exists = rec.line_ids.filtered(
                            lambda line: line.name and line.name.find('Tunisia Tax') == 0)
                        total_balance = sum(other_lines.mapped('balance')) - amount
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        dict1 = {
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        }
                        dict2 = {
                            'debit': total_balance < 0.0 and -total_balance or 0.0,
                            'credit': total_balance > 0.0 and total_balance or 0.0,
                        }
                        rec.line_ids = [(1, already_exists.id, dict1), (1, terms_lines.id, dict2)]

            elif rec.fiscal_position_id.stamp_tax_id.amount <= 0:
                already_exists = rec.line_ids.filtered(
                    lambda line: line.name and line.name.find('Tunisia Tax') == 0)
                if already_exists:
                    rec.line_ids -= already_exists
                    terms_lines = rec.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                    other_lines = rec.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                    total_balance = sum(other_lines.mapped('balance'))
                    total_amount_currency = sum(other_lines.mapped('amount_currency'))
                    terms_lines.update({
                        'amount_currency': -total_amount_currency,
                        'debit': total_balance < 0.0 and -total_balance or 0.0,
                        'credit': total_balance > 0.0 and total_balance or 0.0,
                    })
