from openerp import api, exceptions, fields, models, _
import openerp.addons.decimal_precision as dp


class AssignAnalyticAccount(models.TransientModel):
    _name = "ccrm.stock_quant_assign_analytic"
    _description = "Quant Assign Analytic"

    quant_ids = fields.Many2many('stock.quant', string='Items')

    analytic_account_id = fields.Many2one('account.analytic.account', string='Centru de Cost',
                                          domain=[('account_type', '!=', 'closed')])

    quantity = fields.Float('Cantitate', default=0.0)

    single_quant = fields.Boolean('Single Item', default=False)

    @api.model
    def default_get(self, fields):
        res = super(AssignAnalyticAccount, self).default_get(
            fields)
        quant_obj = self.env['stock.quant']
        quant_ids = self.env.context['active_ids'] or []
        active_model = self.env.context['active_model']

        if not quant_ids:
            return res
        assert active_model == 'stock.quant', \
            'Bad context propagation'

        res['single_quant'] = len(quant_ids) == 1
        res['quant_ids'] = [(6, None, quant_ids)]

        if len(quant_ids) == 1:
            res['quantity'] = quant_obj.browse(quant_ids)[0].qty
        return res

    @api.multi
    def assign_analytic_account(self):
        if len(self.quant_ids.ids) == 1:
            if 0 < self.quantity and self.quantity < self.quant_ids.qty:
                self.env['stock.quant']._quant_split(self.quant_ids, self.quantity)
            self.env['stock.quant'].assign_analytic_account(self.quant_ids, self.analytic_account_id)
        else:
            for quant in self.quant_ids:
                self.env['stock.quant'].assign_analytic_account(quant, self.analytic_account_id)


# class AssignAnalyticAccountItem(models.TransientModel):
#     _name = "cost_center_removal_strategy.stock_quant_assign_analytic_item_i"
#     _description = "Quant Assign Analytic Item"

#     wiz_id = fields.Many2one(comodel_name='cost_center_removal_strategy.stock_quant_assign_analytic',
#                              string='Wizard', required=True, ondelete='cascade', readonly=True)
#     quant_id = fields.Many2one('stock.quant', string='Quant', required=True, readonly=True)