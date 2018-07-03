from openerp import api, models

class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def _cc_removal_get_analytic_accounts_to_pass(self):
        self.ensure_one()
        return  self.analytic_account_id and [self.analytic_account_id.id] or None

    def action_assign(self, cr, uid, ids, context=None):
        ctx = context.copy() or {}
        for id in ids:
            move = self.pool['stock.move'].browse(cr, uid, id, context=context)
            ctx['cc_removal_analytics'] = move._cc_removal_get_analytic_accounts_to_pass()
            super(StockMove, self).action_assign(cr, uid, [id], context=ctx)

    @api.model
    def quants_move(self, quants, move, location_to, location_from=False,
                    lot_id=False, owner_id=False, src_package_id=False, dest_package_id=False):
        removal_strategy = self.env['stock.location'].get_removal_strategy(cr, uid, move.location_id, move.product_id)
        if removal_strategy == 'cost_center' and move.analytic_account_id == None:
            raise ValidationError('Centrul de Cost nu este setat in miscarea produsului %s' % (move.product_id.name,))

        for quant in quants:
            if removal_strategy == 'cost_center' and quant.analytic_account_id != move.analytic_account_id:
                raise ValidationError('Centrul de Cost al produsului %s nu corespunde cu centrul de cost al miscarii.' % (quant.product_id.name,))
        super(StockMove, self).quants_move(quants, move, location_to, location_from=location_from,
                    lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id, dest_package_id=dest_package_id)