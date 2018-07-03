from openerp import api, fields, models
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def apply_removal_strategy(self, location, product, quantity, domain, removal_strategy, context=None):
        if removal_strategy == 'cost_center':
            order = 'in_date, id'
            if self._context.get('cc_removal_analytics', None):
                order = 'analytic_account_id, in_date, id'
                domain += [('analytic_account_id', 'in', self._context['cc_removal_analytics' ])]

            result = self._quants_get_order(location, product, quantity, domain, order)
            return self._apply_custom_post_order(result)
        return super(StockQuant, self).apply_removal_strategy(location, product, quantity, domain, removal_strategy)

    @api.model
    def _apply_custom_post_order(self, result):
        if self._context.get('cc_removal_analytics', None):
            def _cmp_func(item1, item2):
                if not (item1[0] and item2[0]):
                    return 1

                idx1 = self._context['cc_removal_analytics'].index(item1[0].analytic_account_id.id)
                idx2 = self._context['cc_removal_analytics'].index(item2[0].analytic_account_id.id)
                if idx1 != idx2:
                    return idx1 - idx2

                in_date1 = datetime.strptime(item1[0].in_date, DEFAULT_SERVER_DATETIME_FORMAT)
                in_date2 = datetime.strptime(item2[0].in_date, DEFAULT_SERVER_DATETIME_FORMAT)
                return -1 if  in_date1 <= in_date2 else 1

            ordered_result = sorted(result, cmp=_cmp_func)
            return ordered_result
        return result
