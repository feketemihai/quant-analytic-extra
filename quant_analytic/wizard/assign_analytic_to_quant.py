from openerp import api, exceptions, fields, models, _
import openerp.addons.decimal_precision as dp


class AssignAnalyticAccount(models.TransientModel):
    _name = "quant_analytic.stock_quant_assign_analytic"
    _description = "Quant Assign Analytic"

    item_ids = fields.One2many('quant_analytic.stock_quant_assign_analytic_item',
                               'wiz_id', string='Items')

    analytic_account_id = fields.Many2one('account.analytic.account', string='Centru de Cost',
                                          domain=[('type', 'not in', ('view', 'template'))])

    quantity = fields.Float('Cantitate', default=0.0)

    single_quant = fields.Boolean('Single Item', default=False)

    @api.model
    def _prepare_item(self, quant):
        return {
            'quant_id': quant.id
        }

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
        items = []
        for line in quant_obj.browse(quant_ids):
            items.append([0, 0, self._prepare_item(line)])
        res['item_ids'] = items

        if len(items) == 1:
            res['quantity'] = quant_obj.browse(quant_ids)[0].qty
        return res

    @api.multi
    def assign_analytic_account(self):
        if len(self.item_ids.ids) == 1:
            if 0 < self.quantity and self.quantity < self.item_ids.quant_id.qty:
                self.env['stock.quant']._quant_split(self.item_ids.quant_id, self.quantity)
            self.env['stock.quant'].assign_analytic_account(self.item_ids.quant_id, self.analytic_account_id)
        else:
            for item in self.item_ids:
                quant = item.quant_id
                self.env['stock.quant'].assign_analytic_account(quant, self.analytic_account_id)


class AssignAnalyticAccountItem(models.TransientModel):
    _name = "quant_analytic.stock_quant_assign_analytic_item"
    _description = "Quant Assign Analytic Item"

    wiz_id = fields.Many2one('quant_analytic.stock_quant_assign_analytic',
                             string='Wizard', required=True, ondelete='cascade', readonly=True)
    quant_id = fields.Many2one('stock.quant', string='Quant', required=True, readonly=True)
