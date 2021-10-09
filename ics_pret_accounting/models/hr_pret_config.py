from odoo import models, fields, api, _


class AccConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    pret_approve = fields.Boolean(default=False, string="Approbation du service comptabilité",
                                  help="pret Approval from account manager")

    @api.model
    def get_values(self):
        res = super(AccConfig, self).get_values()
        res.update(
            pret_approve=self.env['ir.config_parameter'].sudo().get_param('account.pret_approve')
        )
        return res

    
    def set_values(self):
        super(AccConfig, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('account.pret_approve', self.pret_approve)

