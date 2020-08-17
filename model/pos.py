from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ProfitPoSReport(models.TransientModel):
    _name = 'pos.report'

    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date", required=True)
    type_report = fields.Selection(
        [('detail', 'PoS Profit Detail'), ('summary','PoS Profit Rekap')], 
        string="Tipe Report",
        default='summary' 
    )

    @api.multi
    def print_profit_pos_report(self):
        sessions = self.env['pos.session'].search(
            [ 
                ('stop_at', '<=', self.end_date),
                ('stop_at', '>=', self.start_date),
                ('state', '=', 'closed'),
            ], 
            order="stop_at asc")
    
        session_data = []
        for session in sessions:
            temp = []
            temp_trans = []
            transactions = self.env['pos.order'].search(
                [
                    ('session_id', '=', session.name),
                    ('state', '=', 'done'),
                ]
            )

            total_hpp_transaction = 0
            for transaction in transactions:
                total_hpp_product = 0
                trans_data = []
                trans_line = []

                for line in transaction.lines:
                    lines = []
                    modal = line.product_id.product_tmpl_id.standard_price
                    
                    uom = line.uom_id.name

                    if(line.product_id.product_tmpl_id.uom_id.factor):
                        ratio_uom = line.product_id.product_tmpl_id.uom_id.factor
                    else:
                        ratio_uom = 1
                    
                    purchase_uom = line.product_id.product_tmpl_id.uom_po_id.factor_inv
                    qty = line.qty
                    if(uom == ""):
                        hpp_product = modal*qty*ratio_uom*purchase_uom
                    else:
                        hpp_product = modal*qty
                        uom = line.product_id.product_tmpl_id.uom_id.name
                    
                    total_hpp_product += hpp_product

                    lines.append(line.product_id.name)
                    lines.append(uom)
                    lines.append(qty)
                    lines.append(line.discount)
                    lines.append(line.price_subtotal_incl)
                    lines.append(hpp_product)
                    trans_line.append(lines)

                amount_total = transaction.amount_total
                hpp_transaction = total_hpp_product
                margin_transaction = amount_total - total_hpp_product

                if self.type_report == 'detail':
                    trans_data.append(transaction.pos_reference)
                    trans_data.append(trans_line)
                    trans_data.append(amount_total)
                    trans_data.append(hpp_transaction)
                    trans_data.append(margin_transaction)
            
                temp_trans.append(trans_data)

                total_hpp_transaction += hpp_transaction

            hpp_session = total_hpp_transaction

            temp.append(session.name) #0
            temp.append(session.user_id.name) #1
            temp.append(session.stop_at) #2
            temp.append(hpp_session) #3
            temp.append(temp_trans) #4
            
            total_trans = 0
            for statement in session.statement_ids:
                temp.append(statement.total_entry_encoding)
                total_trans += statement.total_entry_encoding

            temp.append(total_trans)
            temp.append(self.type_report)
            
            session_data.append(temp)

        datas = {
            'ids': self.ids,
            'model': 'pos.report',
            'form': session_data,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env['report'].get_action(self,'profit_pos_report.pos_report_temp', data=datas)
