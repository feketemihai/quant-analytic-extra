from openerp import api, fields, models

class StockQuant(models.Model):
    _inherit = "stock.quant"


    @api.model
    def apply_removal_strategy(self, quantity, move, ops=False, domain=None, removal_strategy='fifo',):
        if removal_strategy == 'cost_center':
            order = 'in_date, id'
            if self._context.get('cc_removal_analytics', None):
                order = 'analytic_account_id, in_date, id'
                domain += [('analytic_account_id', 'in', self._context['cc_removal_analytics' ])]
            return self._quants_get_order(quantity, move, ops=ops, domain=domain, orderby=order)
        return super(StockQuant, self).apply_removal_strategy(quantity, move, ops=ops, domain=domain, removal_strategy=removal_strategy)

    @api.model
    def _apply_custom_post_order(self, result):
        if self._context.get('cc_removal_analytics', None):
            def _cmp_func(item1, item2):
                return self._context['cc_removal_analytics'].index(item1[0].analytic_account_id.id) - \
                    self._context['cc_removal_analytics'].index(item2[0].analytic_account_id.id)

            ordered_result = sorted(result, cmp=_cmp_func)
            return ordered_result
        return super(StockQuant, self)._apply_custom_post_order(result)

    @api.model
    def _quants_get_order(self, quantity, move, ops=False, domain=[], orderby='in_date'):
        res = super(StockQuant, self)._quants_get_order(quantity, move, ops=ops, domain=domain, orderby=orderby)
        return self._apply_custom_post_order(res)
