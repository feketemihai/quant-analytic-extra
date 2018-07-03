from openerp import api, fields, models


class StockQuant(models.Model):

    _inherit = "stock.quant"

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account',
        domain=[('account_type', '=', 'normal')], copy=True)

    @api.model
    def _quant_create(self, qty, move, lot_id=False, owner_id=False, src_package_id=False, dest_package_id=False,
                      force_location_from=False, force_location_to=False):
        qty = super(StockQuant, self)._quant_create(qty, move, lot_id=lot_id, owner_id=owner_id,
                                                     src_package_id=src_package_id, dest_package_id=dest_package_id,
                                                     force_location_from=force_location_from,
                                                     force_location_to=force_location_to)

        qty.analytic_account_id = move.analytic_account_id
        return qty

    @api.cr_uid_ids_context
    def _quants_merge(self, cr, uid, solved_quant_ids, solving_quant, context=None):
        super(StockQuant, self)._quants_merge(cr, uid, solved_quant_ids, solving_quant, context=context)
        if len(solved_quant_ids) == 1:
            solved_quant = self.browse(cr, uid, solved_quant_ids, context=context)
            solved_quant.cost = solving_quant.cost
            if not solved_quant.analytic_account_id:
                solved_quant.analytic_account_id = solving_quant.analytic_account_id

    def _quant_split(self, cr, uid, quant, qty, context=None):
        new_quant = super(StockQuant, self)._quant_split(cr, uid, quant, qty, context=None)
        if new_quant:
            new_quant.analytic_account_id = quant.analytic_account_id
        return new_quant

    @api.model
    def _prepare_journal_item(self, quant, amount, product, qty, analytic_account, account):
        return {'name': product.name,
                'account_id': analytic_account.id,
                'user_id': self.env.user.id,
                'product_id': product.id,
                'unit_amount': qty,
                'amount': amount,
                'product_uom_id': product.uom_id.id,
                'general_account_id': account and account.id or None,
                'date': fields.Date.today()
        }

    @api.model
    def assign_analytic_account(self, quant, analytic_account_id):
        if analytic_account_id and quant.analytic_account_id:
            if self._context.get('register_journal_item', False):
                analytic_line_from = self._prepare_journal_item(quant, quant.cost * quant.qty, quant.product_id, quant.qty, quant.analytic_account_id, None)
                self.env['account.analytic.line'].create(analytic_line_from)

            if self._context.get('register_journal_item', False):
                analytic_line_to = self._prepare_journal_item(quant, -quant.cost * quant.qty, quant.product_id, quant.qty, analytic_account_id, None)
                self.env['account.analytic.line'].create(analytic_line_to)

        quant.analytic_account_id = analytic_account_id
