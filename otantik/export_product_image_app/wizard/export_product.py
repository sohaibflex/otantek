# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime
import xlsxwriter
import base64
import io
from io import BytesIO
from PIL import Image

class ExportProduct(models.TransientModel):
	_name = 'export.product'
	_description = 'Export Product Report'
	
	file = fields.Binary("Download Excel File")
	file_name = fields.Char(string="File Name")


	def resize_image_data(self, file_path, bound_width_height):
		# get the image and resize it
		im = Image.open(file_path)
		im.thumbnail(bound_width_height, Image.ANTIALIAS)  # ANTIALIAS is important if shrinking

		# stuff the image data into a bytestream that excel can read
		im_bytes = BytesIO()
		im.save(im_bytes, format='PNG')
		return im_bytes

	def export_product_xls(self):
		name_of_file = 'Export Product Information.xls'
		file_path = 'Export Product Information' + '.xls'
		workbook = xlsxwriter.Workbook('/tmp/'+file_path)
		worksheet = workbook.add_worksheet('Export Product Information')
		header_format = workbook.add_format({'bold': True,'valign':'vcenter','font_size':16,'align': 'center','bg_color':'#D8D8D8'})
		title_format = workbook.add_format({'border': 1,'bold': True, 'valign': 'vcenter','align': 'center', 'font_size':14,'bg_color':'#D8D8D8'})
		cell_wrap_format_bold = workbook.add_format({'border': 1, 'bold': True,'valign':'vjustify','valign':'vcenter','align': 'center','font_size':12,'bg_color':'#D8D8D8'}) ##E6E6E6
		cell_wrap_format = workbook.add_format({'border': 1,'valign':'vjustify','valign':'vcenter','align': 'left','font_size':12,}) ##E6E6E6
		cell_wrap_format_right = workbook.add_format({'border': 1,'valign':'vjustify','valign':'vcenter','align': 'right','font_size':12,}) ##E6E6E6
		cell_text_wrap_format = workbook.add_format({'text_wrap': True, 'border': 1,'valign':'vjustify','valign':'vcenter','align': 'left','font_size':12,}) ##E6E6E6
		cell_text_wrap_format.set_text_wrap()
		#Merge Row Columns
		TITLEHEDER = 'Export Product Information' 

		worksheet.set_column(0, 0, 19)
		worksheet.set_column(1, 2, 25)
		worksheet.set_column(3, 3, 25)
		worksheet.set_column(4, 4, 17)
		worksheet.set_column(5, 5, 17)
		worksheet.set_column(10, 10, 10)

		active_ids = self._context['active_ids']
		products = self.env['product.product'].browse(active_ids)
		worksheet.merge_range(1, 0, 0, 5, TITLEHEDER,header_format)
		rowscol = 1
		worksheet.set_row(rowscol,20)
		worksheet.write(rowscol + 2, 0, 'Internal Reference', cell_wrap_format_bold)
		worksheet.write(rowscol + 2, 1, 'Product Name', cell_wrap_format_bold)
		worksheet.write(rowscol + 2, 2, 'Category',cell_wrap_format_bold)
		worksheet.write(rowscol + 2, 3, 'Image', cell_wrap_format_bold)
		worksheet.write(rowscol + 2, 4, 'Sale Price', cell_wrap_format_bold)
		worksheet.write(rowscol + 2, 5, 'Cost', cell_wrap_format_bold)
		rows = (rowscol + 3)
		for item in products:
			worksheet.set_row(rows,30)
			worksheet.write(rows, 0, item.default_code or '', cell_wrap_format)
			worksheet.write(rows, 1, item.name or '', cell_text_wrap_format)
			worksheet.write(rows, 2, item.categ_id.complete_name or '', cell_text_wrap_format)
			if item.image_1920:
				prod_img = BytesIO(base64.b64decode(item.image_1920))
				image_path = 'product_image_png.png'
				bound_width_height = (270, 90)
				image_data = self.resize_image_data(prod_img, bound_width_height)
				worksheet.insert_image(rows, 3, "product_image.png", {'image_data': image_data})
				worksheet.set_row(rows,85)
			worksheet.write(rows, 4, item.lst_price or '', cell_text_wrap_format)
			worksheet.write(rows, 5, str('%.2f' % item.standard_price or ''), cell_wrap_format_right)
			rows = rows+1
			rowscol = rows

		workbook.close()
		export_id = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())
		result_id = self.env['export.product'].create({'file': export_id ,'file_name': name_of_file})
		return {
				'name': 'Export Product with Images',
				'view_mode': 'form',
				'res_id': result_id.id,
				'res_model': 'export.product',
				'view_type': 'form',
				'type': 'ir.actions.act_window',
				'target': 'new',
			}
