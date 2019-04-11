from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime


# Report class
class ProductAgeing(models.Model):
    _name = 'product.ageing'

    # From Date field
    from_date = fields.Datetime(string='From Date', required=True)
    # Inventory field
    location_id = fields.Many2many('stock.location', string="Location",
                                   domain="[('usage','=','internal')]")
    # Product category field
    product_category = fields.Many2many('product.category', string="Category")
    # Product aging result
    product_ageing_result = fields.One2many('ageing.result', 'ageing_result')
    # Time period
    interval = fields.Integer(string="Interval(days)", default=30, required=True)
    # Time period wise location
    set_internal_location = fields.Boolean(string='All Internal Locations')
    # Setting up all product categories
    set_all_product_categories = fields.Boolean(string='Get all categories')
    # Type of th report
    report_type_selection = fields.Selection([
        ('quant', 'Quantity'),
        ('value', 'Value'),
        ], string='Report Type', default='value')

    @api.multi
    def compute_ageing(self):
        """Get the report data and do the computation for each and every product in the stock and
        divided it into the relevant time period"""

        self.env['ageing.result'].search([]).unlink()

        # Get current company id
        current_compnay_id = self.env.user.company_id.id
        # Get products that related to the company
        products = self.env['product.product'].search([('company_id', '=', current_compnay_id)])

        # Get all product category
        if self.set_all_product_categories:
            get_all_categories = self.env['product.category'].search([]).ids
        else:
            get_all_categories = self.product_category.ids
        # filter the product according the domain
        filtered_products = products.filtered(lambda category: category.categ_id.id in get_all_categories)

        # Get internal location that related to specific company Id and Usage ID
        if self.set_internal_location:
            get_internal_loc = self.env['stock.location'].search(
                [('company_id', '=', current_compnay_id), ('usage', '=', 'internal')]).ids

        else:
            get_internal_loc = self.location_id.ids

        # Get the final move line
        final_move_list = []
        for product in filtered_products:
            for location in get_internal_loc:
                # Get all outgoing moves
                out_moves = self.env['stock.move'].search(
                    [('product_id', '=', product.id), ('location_id', '=', location),
                     ('date', '<=', self.from_date)]).filtered(lambda move: move.state == 'done').sorted(
                    key=lambda x: x.date)
                # Get all incoming moves
                in_moves = self.env['stock.move'].search(
                    [('product_id', '=', product.id), ('location_dest_id', '=', location),
                     ('date', '<=', self.from_date)]).filtered(lambda move: move.state == 'done').sorted(
                    key=lambda x: x.date)

                out_qty = 0
                out_value = 0
                for out_move in out_moves:
                    out_qty += out_move.product_qty
                    out_value += out_move.value

                candidate_moves = in_moves
                for in_move in in_moves:
                    move_qty = in_move.product_qty
                    move_value = in_move.value

                    if out_qty > 0:

                        if move_qty <= out_qty:
                            candidate_moves -= in_move
                            out_qty -= move_qty
                            out_value -= move_value

                        elif move_qty > out_qty:
                            # Set the candidate move line
                            candidate_moves -= in_move
                            data = {
                                'move': in_move,
                                'date': datetime.datetime.strptime(str(in_move.date), '%Y-%m-%d %H:%M:%S').date(),
                                'qty': in_move.product_qty - out_qty,
                                'value': in_move.value - out_value
                            }
                            final_move_list.append(data)

                            out_qty = 0

                # If it is a candidate move, get the move line
                for candidate_move in candidate_moves:
                    data = {
                        'move': candidate_move,
                        'qty': candidate_move.product_qty,
                        'value': candidate_move.value,
                        'date': datetime.datetime.strptime(str(candidate_move.date), '%Y-%m-%d %H:%M:%S').date()
                    }

                    final_move_list.append(data)

        product_list = []
        items = {}

        for final_products in final_move_list:
            """Set the dictionary with final computed values of the report"""
            date_one = datetime.datetime.strptime(str(self.from_date), '%Y-%m-%d %H:%M:%S').date()
            # Final product move that not in product list
            if final_products['move'].product_id.id not in product_list:

                product_list.append(final_products['move'].product_id.id)
                # Get the date to
                date_two = datetime.datetime.strptime(str(final_products['date']), '%Y-%m-%d').date()
                no_days = (date_one - date_two).days

                quantity = [0, 0, 0, 0, 0, 0, 0]
                value = [0, 0, 0, 0, 0, 0, 0]

                # Time period wise categorized product quantity and product value

                # 0-30 days
                if no_days <= self.interval:
                    quantity[0] += final_products['qty']
                    value[0] += final_products['value']
                # 31-60 days
                if no_days > self.interval and no_days <= self.interval * 2:
                    quantity[1] += final_products['qty']
                    value[1] += final_products['value']
                # 61-90 days
                if no_days > self.interval * 2 and no_days <= self.interval * 3:
                    quantity[2] += final_products['qty']
                    value[2] += final_products['value']
                # 91-120 days
                if no_days > self.interval * 3 and no_days <= self.interval * 4:
                    quantity[3] += final_products['qty']
                    value[3] += final_products['value']
                # 121-240 days
                if no_days > self.interval * 4 and no_days <= self.interval * 8:
                    quantity[4] += final_products['qty']
                    value[4] += final_products['value']
                # 241-360 days
                if no_days > self.interval * 8 and no_days <= self.interval * 12:
                    quantity[5] += final_products['qty']
                    value[5] += final_products['value']
                # Over 360 days
                if no_days > self.interval * 12:
                    quantity[6] += final_products['qty']
                    value[6] += final_products['value']

                total_quant = final_products['qty']
                total_val = final_products['value']

                """Setting up the dictionary with product, product location, Product UOM, Product quantity,
                 Product Value and the total value"""
                data = {
                    'product': final_products['move'].product_id.name,
                    'product_desc': final_products['move'].product_id.description,
                    'product_uom': final_products['move'].product_uom.name,
                    'quantity': quantity,
                    'value': value,
                    'total_quant': total_quant,
                    'total_val': total_val
                }

                items[final_products['move'].product_id.id] = data

            # Final product move that in product list
            elif final_products['move'].product_id.id in product_list:
                date_two = datetime.datetime.strptime(str(final_products['date']), '%Y-%m-%d').date()
                no_days = (date_one - date_two).days

                # 0-30 days
                if no_days <= self.interval:
                    items[final_products['move'].product_id.id]['quantity'][0] += final_products['qty']
                    items[final_products['move'].product_id.id]['total_quant'] += final_products['qty']

                    items[final_products['move'].product_id.id]['value'][0] += final_products['value']
                    items[final_products['move'].product_id.id]['total_val'] += final_products['value']

                # 31-60 days
                if no_days > self.interval and no_days <= self.interval * 2:
                    items[final_products['move'].product_id.id]['quantity'][1] += final_products['qty']
                    items[final_products['move'].product_id.id]['total_quant'] += final_products['qty']

                    items[final_products['move'].product_id.id]['value'][1] += final_products['value']
                    items[final_products['move'].product_id.id]['total_val'] += final_products['value']

                # 61-90 days
                if no_days > self.interval * 2 and no_days <= self.interval * 3:
                    items[final_products['move'].product_id.id]['quantity'][2] += final_products['qty']
                    items[final_products['move'].product_id.id]['total_quant'] += final_products['qty']

                    items[final_products['move'].product_id.id]['value'][2] += final_products['value']
                    items[final_products['move'].product_id.id]['total_val'] += final_products['value']

                # 91-120 days
                if no_days > self.interval * 3 and no_days <= self.interval * 4:
                    items[final_products['move'].product_id.id]['quantity'][3] += final_products['qty']
                    items[final_products['move'].product_id.id]['total_quant'] += final_products['qty']

                    items[final_products['move'].product_id.id]['value'][3] += final_products['value']
                    items[final_products['move'].product_id.id]['total_val'] += final_products['value']

                # 121-240 days
                if no_days > self.interval * 4 and no_days <= self.interval * 8:
                    items[final_products['move'].product_id.id]['quantity'][4] += final_products['qty']
                    items[final_products['move'].product_id.id]['total_quant'] += final_products['qty']

                    items[final_products['move'].product_id.id]['value'][4] += final_products['value']
                    items[final_products['move'].product_id.id]['total_val'] += final_products['value']

                # 241-360 days
                if no_days > self.interval * 8 and no_days <= self.interval * 12:
                    items[final_products['move'].product_id.id]['quantity'][5] += final_products['qty']
                    items[final_products['move'].product_id.id]['total_quant'] += final_products['qty']

                    items[final_products['move'].product_id.id]['value'][5] += final_products['value']
                    items[final_products['move'].product_id.id]['total_val'] += final_products['value']

                # Over 360 days
                if no_days > self.interval * 12:
                    items[final_products['move'].product_id.id]['quantity'][6] += final_products['qty']
                    items[final_products['move'].product_id.id]['total_quant'] += final_products['qty']

                    items[final_products['move'].product_id.id]['value'][6] += final_products['value']
                    items[final_products['move'].product_id.id]['total_val'] += final_products['value']

        id_list = []
        """Set the record set and pass it to the QWEB will well arranged data"""
        for ageing_product in items.values():
            line_id = self.env['ageing.result'].create({
                'product_name': ageing_product['product'],
                'product_desc': ageing_product['product_desc'],
                'product_uom': ageing_product['product_uom'],
                'range_one': ageing_product['quantity'][0],
                'range_two': ageing_product['quantity'][1],
                'range_three': ageing_product['quantity'][2],
                'range_four': ageing_product['quantity'][3],
                'range_five': ageing_product['quantity'][4],
                'range_six': ageing_product['quantity'][5],
                'range_seven': ageing_product['quantity'][6],
                'value_one': ageing_product['value'][0],
                'value_two': ageing_product['value'][1],
                'value_three': ageing_product['value'][2],
                'value_four': ageing_product['value'][3],
                'value_five': ageing_product['value'][4],
                'value_six': ageing_product['value'][5],
                'value_seven': ageing_product['value'][6],
                'total_quantity': ageing_product['total_quant'],
                'total_value': ageing_product['total_val']
            })
            id_list.append(line_id.id)

        self.product_ageing_result = id_list
        return self.env.ref('product_ageing_report.action_report_product_ageing').report_action(self)


# Aging result class
class AgeingResult(models.Model):
    _name = 'ageing.result'

    # Product name
    product_name = fields.Char(string='Product')
    # Product description
    product_desc = fields.Char(string='Description')
    # Product unit of meassure
    product_uom = fields.Char(string='Unit of Measure')
    # Quantity range
    range_one = fields.Float(string='Range one')
    range_two = fields.Float(string='Range one')
    range_three = fields.Float(string='Range one')
    range_four = fields.Float(string='Range one')
    range_five = fields.Float(string='Range one')
    range_six = fields.Float(string='Range one')
    range_seven = fields.Float(string='Range one')
    # Value range
    value_one = fields.Float(string='value one')
    value_two = fields.Float(string='value one')
    value_three = fields.Float(string='value one')
    value_four = fields.Float(string='value one')
    value_five = fields.Float(string='value one')
    value_six = fields.Float(string='value one')
    value_seven = fields.Float(string='value one')
    # Total quantity
    total_quantity = fields.Float(string='Range one')
    # Total Value
    total_value = fields.Float(string='Range one')
    # Final aging result
    ageing_result = fields.Many2one('product_ageing_result')
