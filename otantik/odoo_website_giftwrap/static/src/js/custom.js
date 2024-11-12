
//console.log("odoo_website_giftwrap custom js caleedddddddddddddddddddddddddddddddddd")
odoo.define('odoo_website_giftwrap.odoo_website_giftwrap', function(require) {
	"use strict";

	var core = require('web.core');
	var _t = core._t;
	var ajax = require('web.ajax');
	var rpc = require('web.rpc');

	$(document).ready(function() {
		var oe_website_sale = this;
		
		var $giftwrap = $("#row_data");

		$('.item_image').each(function(){

			$('.raghav').removeClass('raghav');
            $("#myPack").find(".item_image").first().addClass('raghav');
			$(this).on('click',function () {
				if ( $(this).hasClass('raghav') )
				{
					$('.raghav').removeClass('raghav');
					$('#giftwrapbutton').addClass('d-none');
				}
				else{
					$('.raghav').removeClass('raghav');
					$(this).addClass('raghav');
					$('#giftwrapbutton').removeClass('d-none');
				}
			});
		});

		$('#giftwrapbutton').on('click', function() {
				var notes = $("#notes").val();
				var product = $(".raghav").data('id');
                ajax.jsonRpc('/shop/cart/giftwrap', 'call', {
					'notes': notes,
					'product':product,
				}).then(function (notes) {
				location.reload();
//					rpc.query({
//					model: 'website',
//					method: 'get_gift_product',
//					args: [product],
//					}).then(function (data) {
//						location.reload();
//					});

				});





								
				
			});

		// $('.oe_website_sale').each(function() {
		// 	var oe_website_sale = this;

			

			
		// 	// $(".js_add_cart_json_new").click(function(ev){
		// 	// 	ev.preventDefault();
		// 	// 	////div[hasclass('oe_cart')] console.log("submit-billing-btnnnnnnnnnnnnnnnnnnnnnnnnn",$(this));
		// 	// 	$(this).closest('tr').find('.js_quantity').val(0).trigger('change');
		// 	// });
						
						
					
		// });		
		
		
	});
});;
