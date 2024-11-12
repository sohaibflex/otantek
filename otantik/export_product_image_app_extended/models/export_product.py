import xlsxwriter
import base64
import io
from io import BytesIO
from PIL import Image

from odoo import models, fields, api


class InheritExportProduct(models.TransientModel):
    _inherit = 'export.product'

    def export_product_xls(self):

        name_of_file = 'Export Product Information.xls'
        file_path = 'Export Product Information' + '.xls'
        workbook = xlsxwriter.Workbook('/tmp/' + file_path,{'strings_to_numbers': True})
        worksheet = workbook.add_worksheet('Export Product Information')
        worksheet.freeze_panes(1, 0)
        header_format = workbook.add_format(
            {'bold': True, 'valign': 'vcenter', 'font_size': 16, 'align': 'center', 'bg_color': '#D8D8D8'})
        title_format = workbook.add_format(
            {'border': 1, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'font_size': 14, 'bg_color': '#D8D8D8'})
        cell_wrap_format_bold = workbook.add_format(
            {'border': 1, 'bold': True, 'valign': 'vjustify', 'valign': 'vcenter', 'align': 'center', 'font_size': 12,
             'bg_color': '#D8D8D8'})  ##E6E6E6
        cell_wrap_format = workbook.add_format(
            {'border': 1, 'valign': 'vjustify', 'valign': 'vcenter', 'align': 'left', 'font_size': 12, })  ##E6E6E6
        cell_wrap_format_right = workbook.add_format(
            {'border': 1, 'valign': 'vjustify', 'valign': 'vcenter', 'align': 'right', 'font_size': 12, })  ##E6E6E6
        cell_text_wrap_format = workbook.add_format(
            {'text_wrap': True, 'border': 1, 'valign': 'vjustify', 'valign': 'vcenter', 'align': 'left',
             'font_size': 12, })  ##E6E6E6
        cell_text_wrap_format.set_text_wrap()
        # Merge Row Columns
        TITLEHEDER = 'Export Product Information'

        worksheet.set_column(0, 0, 19)
        worksheet.set_column(1, 2, 25)
        worksheet.set_column(3, 3, 25)
        worksheet.set_column(4, 4, 17)
        worksheet.set_column(5, 5, 17)
        worksheet.set_column(6, 6, 20)
        worksheet.set_column(10, 10, 10)

        active_ids = self._context['active_ids']
        products = self.env['product.product'].browse(active_ids)
        # worksheet.merge_range(1, 0, 0, 15, TITLEHEDER, header_format)
        row_header_gap = 0
        static_pointer = 0
        worksheet.set_row(row_header_gap, 20)
        worksheet.write(row_header_gap , static_pointer +0, 'Internal Reference', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +1, 'Product EN', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +2, 'Description EN', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +3, 'Product AR', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +4, 'Description AR', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +5, 'Category', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +6, 'Image', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +7, 'Sale Price', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +8, 'Cost', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +9, 'Available Quantity', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +10, 'Collection', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +11, 'Color', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +12, 'Material', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +13, 'Capacity', cell_wrap_format_bold)
        worksheet.write(row_header_gap , static_pointer +14, 'Number Of Pieces', cell_wrap_format_bold)



        header_pointer = 15
        pricelist_start = header_pointer
        product_pricelists = self.env['product.pricelist'].search([])
        if product_pricelists:
            for pricelist in product_pricelists:
                worksheet.set_column(header_pointer, 20, 20)
                worksheet.write(row_header_gap, header_pointer, pricelist.name, cell_wrap_format_bold)
                header_pointer += 1

        # attributes replaces with ot attributes
        # attributes = self.env['product.attribute'].search([])
        # attr_list = []
        # attributes_start = header_pointer
        # for attr in attributes:
        #     attr_list.append(attr.name)
        #     worksheet.set_column(header_pointer, 20, 20)
        #     worksheet.write(row_header_gap, header_pointer, attr.name, cell_wrap_format_bold)
        #     header_pointer += 1
        warehouses = self.env['stock.warehouse'].search([])
        wh_list = []

        wh_start = header_pointer
        for wh in warehouses:
            wh_list.append(wh.name)
            worksheet.set_column(header_pointer, 20, 20)
            worksheet.write(row_header_gap, header_pointer, wh.name, cell_wrap_format_bold)
            header_pointer += 1

        rows = (row_header_gap + 1)
        for item in products:
            worksheet.set_row(rows, 30)
            worksheet.write(rows, static_pointer +0, item.default_code or '', cell_wrap_format)
            worksheet.write(rows, static_pointer +1, item.name or '', cell_text_wrap_format)
            worksheet.write(rows, static_pointer +2, item.description_sale or '', cell_text_wrap_format)
            worksheet.write(rows, static_pointer +3, item.with_context(lang="ar_001").name or '', cell_text_wrap_format)
            worksheet.write(rows, static_pointer +4, item.with_context(lang="ar_001").description_sale or '', cell_text_wrap_format)
            worksheet.write(rows, static_pointer +5, item.categ_id.complete_name or '', cell_text_wrap_format)
            if item.image_1920:
                prod_img = BytesIO(base64.b64decode(item.image_1920))
                image_path = 'product_image_png.png'
                bound_width_height = (270, 90)
                image_data = self.resize_image_data(prod_img, bound_width_height)
                worksheet.insert_image(rows, static_pointer +6, "product_image.png", {'image_data': image_data})
                worksheet.set_row(rows, 85)
            worksheet.write(rows, static_pointer +7, item.lst_price or '', cell_text_wrap_format)
            if self.env.user.has_group('product_cost_security.group_product_cost'):
                worksheet.write(rows, static_pointer +8, str('%.2f' % item.standard_price or ''), cell_wrap_format_right)
            else:
                worksheet.write(rows, static_pointer +8, '', cell_wrap_format_right)
            # for available quantity column:
            available_quantity = 0
            stock_quant = self.env['stock.quant'].search([
                ('product_id', '=', item.id),
                ('location_id.usage', '=', 'internal')
            ])
            if stock_quant:
                for quant in stock_quant:
                    available_quantity += quant.available_quantity
                worksheet.write(rows, static_pointer +9, str(available_quantity or ''), cell_text_wrap_format)
            

            worksheet.write(rows, static_pointer +10, item.ot_collection.name or '', cell_text_wrap_format)
            worksheet.write(rows, static_pointer +11, item.ot_color.name or '', cell_text_wrap_format)
            worksheet.write(rows, static_pointer +12, item.ot_material.name or '', cell_text_wrap_format)
            worksheet.write(rows, static_pointer +13, item.ot_capacity.name or '', cell_text_wrap_format)
            worksheet.write(rows, static_pointer +14, item.ot_pieces.name or '', cell_text_wrap_format)

            # for product price list in header:
            header_pointer = pricelist_start
            # product_pricelists = self.env['product.pricelist'].search([])
            if product_pricelists:
                for pricelist in product_pricelists:
                    # worksheet.set_column(pricelist_colum, 20, 20)
                    # worksheet.write(rowscol + 2, pricelist_colum, pricelist.name, cell_wrap_format_bold)

                    pricelist_value = 0.0
                    price_list_items = self.env['product.pricelist.item'].search([
                        ('product_tmpl_id', '=', item.product_tmpl_id.id),
                        ('pricelist_id', '=', pricelist.id)
                    ])
                    if price_list_items:
                        for price_list_item in price_list_items:
                            pricelist_value += price_list_item.fixed_price
                    worksheet.write(rows, header_pointer, str(pricelist_value or ''), cell_text_wrap_format)
                    # pricelist_value = 0.0
                    header_pointer += 1
            attr_value_list = {}
            for attr in item.product_template_attribute_value_ids :
                attr_value_list[attr.attribute_id.name] = attr.name

            # attributes replaces with ot attributes
            # header_pointer = attributes_start
            # for attr in attr_list:
            #     worksheet.set_column(header_pointer, 20, 20)
            #     worksheet.write(rows, header_pointer,attr_value_list.get(attr) or '', cell_text_wrap_format)
            #     header_pointer += 1
            warehouse_quantity_text = ''
            if item:
                quant_ids = self.env['stock.quant'].search(
                    [('product_id', '=', item[0].id), ('location_id.usage', '=', 'internal')])
                t_warehouses = {}
                for quant in quant_ids:
                    if quant.location_id:
                        if quant.location_id not in t_warehouses:
                            t_warehouses.update({quant.location_id: 0})
                        # Onhand Quantity
                        # t_warehouses[quant.location_id] += quant.quantity
                        t_warehouses[quant.location_id] += quant.available_quantity

                tt_warehouses = {}

                for location in t_warehouses:
                    warehouse = False
                    location1 = location
                    while (not warehouse and location1):
                        warehouse_id = self.env['stock.warehouse'].search(
                            [('lot_stock_id', '=', location1.id)])
                        if len(warehouse_id) > 0:
                            warehouse = True
                        else:
                            warehouse = False
                        location1 = location1.location_id
                    if warehouse_id:
                        if warehouse_id.name not in tt_warehouses:
                            tt_warehouses.update({warehouse_id.name: 0})
                        tt_warehouses[warehouse_id.name] += t_warehouses[location]

                for item in tt_warehouses:
                    if tt_warehouses[item] != 0:
                        warehouse_quantity_text = warehouse_quantity_text + ' ** ' + item + ': ' + str(
                            tt_warehouses[item])
                wh_colum = wh_start
                for wh in wh_list:
                    worksheet.write(rows, wh_colum, str(tt_warehouses.get(wh) or ''), cell_text_wrap_format)
                    wh_colum += 1

            rows = rows + 1
            rowscol = rows

        workbook.close()
        export_id = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())
        result_id = self.env['export.product'].create({'file': export_id, 'file_name': name_of_file})
        return {
            'name': 'Export Product with Images',
            'view_mode': 'form',
            'res_id': result_id.id,
            'res_model': 'export.product',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
