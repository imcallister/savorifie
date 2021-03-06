import itertools
from decimal import Decimal
import logging

import sales_funcs

logger = logging.getLogger('default')

class SaleGLMixin():

    
    def get_all_dates(self):
        return list(set([u.date for u in self.unit_sale.all()]
                        + [pa.date for pa in self.proceedsadjustment_sale.all()]
                        + [st.date for st in self.sales_tax.all()]
                        )
                )

    

    """
    helper funcs
    """

    def COGS(self, date):
        all_items = list(itertools.chain.from_iterable(u.COGS() for u in self.unit_sale.filter(date=date)))
        key_func = lambda x: x['label']
        gps = itertools.groupby(sorted(all_items, key=key_func), key=key_func)
        return dict((k, sum(a['COGS'] for a in v)) for k, v in gps)
    

    def get_COGS_lines(self, date):
        lines = []
        COGS_amounts = self.COGS(date)
        channel_id = self.channel.counterparty.id

        for ii in COGS_amounts:
            inv_acct = sales_funcs.get_inventory_account(ii)
            COGS_acct = sales_funcs.get_COGS_account(ii, channel_id)
            lines.append((inv_acct, -COGS_amounts[ii], self.customer_code.id, []))
            lines.append((COGS_acct, COGS_amounts[ii], self.customer_code.id, []))
        return lines


    
    def get_specialsale_lines(self):
        lines = []
        sample_exp_acct = sales_funcs.get_special_account(self.special_sale)

        # get COGS
        COGS_amounts = self.COGS(self.sale_date)
        for ii in COGS_amounts:
            inv_acct = sales_funcs.get_inventory_account(ii)
            if self.customer_code:
                lines.append((inv_acct, -COGS_amounts[ii], self.customer_code.id, []))
                lines.append((sample_exp_acct, COGS_amounts[ii], self.customer_code.id, []))
            else:
                logger.error('Sale.get_specialsale_lines failed. No customer code. %s' % str(self))
        return lines

    def get_acctrec_lines(self, lines):
        rcvbl = -sum(l[1] for l in lines)
        paid_thru = self.paid_thru.id if self.paid_thru else None
        if paid_thru == 'PAYPAL':
            accts_rec = sales_funcs.get_paypal_acct()
            return [(accts_rec, rcvbl, self.customer_code.id, [])]
        else:
            accts_rec = sales_funcs.get_receiveables_account(self.channel.label, paid_thru)
            return [(accts_rec, rcvbl, self.payee().id, [])]



    # create adjustments GL lines
    def get_channelfee_lines(self, adj):
        lines = []
        channel_id = self.channel.counterparty.id
        if adj.amount != 0:
            channelfees_acct = sales_funcs.get_channelfees_account(channel_id)
            lines.append((channelfees_acct,
                          -Decimal(adj.amount),
                          channel_id, []))
        return lines

    def get_shippingcharge_lines(self, adj):
        lines = []
        if adj.amount != 0:
            shipping_acct = sales_funcs.get_shipping_account()
            lines.append((shipping_acct, -Decimal(adj.amount), self.customer_code.id, []))
        return lines


    def get_giftcardredemption_lines(self, adj):
        lines = []
        if adj.amount != 0:
            giftcard_accrual_acct = sales_funcs.get_giftcard_acct()
            lines.append((giftcard_accrual_acct, Decimal(adj.amount), self.customer_code.id, []))
        return lines

    def get_discount_lines(self, adj):
        lines = []
        discount_acct = sales_funcs.get_discount_account(self.channel.label)
        if adj.amount != 0:
            lines.append((discount_acct, -Decimal(adj.amount), self.customer_code.id, []))
        return lines

    def get_giftwrap_lines(self, adj):
        lines = []
        giftwrap_acct = sales_funcs.get_giftwrap_account()
        if self.gift_wrapping:
            lines.append((giftwrap_acct, -Decimal(adj.amount), self.customer_code.id, []))
        return lines

    def get_payment_lines(self, adj):
        lines = []
        accts_rec = sales_funcs.get_receiveables_account(None, None)
        lines.append((accts_rec, -Decimal(adj.amount), self.customer_code, []))
        return lines


    """
    functions to generate tran lines
    """

    def get_grosssales_lines(self, date):
        lines = []
        channel_id = self.channel.counterparty.id
        if self.customer_code:
            customer_code = self.customer_code.id
            unit_sales = self.unit_sale.filter(date=date)
            for u_sale in unit_sales:
                if u_sale.sku.label == 'GIFTCARD':
                    giftcard_accrual_acct = sales_funcs.get_giftcard_acct()
                    lines .append((giftcard_accrual_acct, - u_sale.quantity * u_sale.unit_price, customer_code, []))
                else:
                    inv_items = u_sale.get_gross_sales()
                    for ii in inv_items:
                        gross_sales_acct = sales_funcs.get_grosssales_account(ii, channel_id)
                        lines.append((gross_sales_acct, -inv_items[ii], customer_code, []))
        else:
            logger.error('Sale.get_grosssales_lines failed. No customer code. %s' % str(self))
        return lines

    def get_adjustment_lines(self, date):
        adjusts = self.proceedsadjustment_sale.filter(date=date)
        
        lines = []
        for adj in adjusts:
            if adj.adjust_type == 'CHANNEL_FEES':
                lines += self.get_channelfee_lines(adj)
            elif adj.adjust_type == 'SHIPPING_CHARGE':
                lines += self.get_shippingcharge_lines(adj)
            elif adj.adjust_type == 'DISCOUNT':
                lines += self.get_discount_lines(adj)
            elif adj.adjust_type == 'GIFTWRAP_FEES':
                lines += self.get_giftwrap_lines(adj)
            elif adj.adjust_type == 'GIFTCARD_REDEMPTION':
                lines += self.get_giftcardredemption_lines(adj)
            elif adj.adjust_type == 'PAYMENT':
                lines += self.get_payment_lines(adj)
        return lines

    def get_salestax_lines(self, date):
        lines = []
        salestax_acct = sales_funcs.get_salestax_account()
        
        sales_taxes = self.sales_tax.filter(date=date)
        tax_collectors = list(set([t.collector.entity for t in sales_taxes]))
        tax_amts = dict((p, 0) for p in tax_collectors)
        for t in sales_taxes:
            tax_amts[t.collector.entity] += Decimal(t.tax)
        for entity in tax_amts:
            lines.append((salestax_acct, -tax_amts[entity], entity, []))
        return lines
