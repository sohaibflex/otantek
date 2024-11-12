odoo.define('sales_modification.gift_note', function (require) {
"use strict";

    $(document).on('click', '.show_gift_text', function(ev) {
            var type = $(this).attr('data-value');
            $('.show_gift_text').addClass('d-none');
            $('.input_main_gift_note').removeClass('d-none');
            $('body').removeClass('gift_box_added_class');

        });


});