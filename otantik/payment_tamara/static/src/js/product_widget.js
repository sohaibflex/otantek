/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('payment_tamara_product_widget.product_widget', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var VariantMixin = require('sale.VariantMixin');

    $(document).ready(function() {
        if ($('.tamara-product-widget').length >0 ){
            ajax.jsonRpc('/product/widget', 'call', {}).then((product_widget)=> {
                    if (product_widget.product_widget){
                        if (window.TamaraProductWidget) { 
                            window.TamaraProductWidget.init({
                           
                            });
                            window.TamaraProductWidget.render()
                        }       
                }
                
            });
        }
    });


    $(document).ready(function() {
        if ($('.tamara-installment-plan-widget').length >0 ){
            ajax.jsonRpc('/product/widget', 'call', {}).then((product_widget)=> {
                    if (product_widget.product_widget){
                        const widgetAmount = $('#order_total').find('.oe_currency_value').text();
                        $('.tamara-installment-plan-widget').attr('data-price',widgetAmount)
                        if (window.TamaraInstallmentPlan) { 
                            window.TamaraInstallmentPlan.init({
                                       
                            });
                            window.TamaraInstallmentPlan.render()
                        }       
                }
                
            });
        }
    });


    const originalOnChangeCombination = VariantMixin._onChangeCombination;
    VariantMixin._onChangeCombination = function (ev, $parent, combination) {
        $('.tamara-product-widget').attr('data-price', combination.price)
        if (window.TamaraProductWidget) { 
            window.TamaraProductWidget.init({
           
            });
            window.TamaraProductWidget.render()
        }  

        originalOnChangeCombination.apply(this, [ev, $parent, combination]);
    };

});

