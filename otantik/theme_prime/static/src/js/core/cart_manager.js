odoo.define('theme_prime.website_cart_manager', function (require) {
'use strict';

    require('website_sale_options.website_sale');
    require('website_sale_stock.VariantMixin');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var QuickViewDialog = require('theme_prime.product_quick_view');
    var wSaleUtils = require('website_sale.utils');
    var CartManagerMixin = require('theme_prime.mixins').CartManagerMixin;

    var _t = core._t;

    function prepareRequestForm(route, params) {
        function _addInput(form, name, value) {
            let param = document.createElement('input');
            param.setAttribute('type', 'hidden');
            param.setAttribute('name', name);
            param.setAttribute('value', value);
            form.appendChild(param);
        }

        let form = document.createElement('form');
        form.setAttribute('action', route);
        form.setAttribute('method', params.method || 'POST');

        if (core.csrf_token) {
            _addInput(form, 'csrf_token', core.csrf_token);
        }

        for (const key in params) {
            const value = params[key];
            if (Array.isArray(value) && value.length) {
                for (const val of value) {
                    _addInput(form, key, val);
                }
            } else {
                _addInput(form, key, value);
            }
        }
        document.body.appendChild(form);
        return $(form);
    }

    publicWidget.registry.WebsiteSale.include(_.extend({}, CartManagerMixin, {

        xmlDependencies: (publicWidget.registry.WebsiteSale.prototype.xmlDependencies || []).concat(['/theme_prime/static/src/xml/frontend/notification_template.xml']),

        init: function () {
            this.dr_cart_flow = odoo.dr_theme_config.cart_flow || 'default';
            return this._super.apply(this, arguments);
        },
        _onProductReady: function () {
            if (this._isDefaultCartFLow() || this.isBuyNow) {
                return this._super.apply(this, arguments);
            }

            /*  We assume is qty selector is not present the it will not have the
                variant selector so `variantSelectorNeeded` variable used to indicate
                that should we open custom selector or not.
            */
            var variantSelectorNeeded = !this.$form.find('input[name="add_qty"]').length;
            if (variantSelectorNeeded) {
                var dialogOptions = {mini: true, size: 'small', add_if_single_variant: true};
                var productID = this.$form.find('.product_template_id').val();
                if (productID) {
                    dialogOptions['productID'] = parseInt(productID);
                } else {
                    dialogOptions['variantID'] = this.rootProduct.product_id;
                }
                this.QuickViewDialog = new QuickViewDialog(this, dialogOptions).open();
                return this.QuickViewDialog;
            }
            return this._customCartSubmit();
        },

        _customCartSubmit: function () {
            var self = this;
            let params = this.rootProduct;
            params.add_qty = params.quantity;
            params.dr_cart_flow = this.dr_cart_flow || 0;

            params.product_custom_attribute_values = JSON.stringify(params.product_custom_attribute_values);
            params.no_variant_attribute_values = JSON.stringify(params.no_variant_attribute_values);

            var $form = prepareRequestForm('/shop/cart/update', params);
            return $form.ajaxSubmit({
                dataType: 'json',
                success: function (data) {
                    if (data) {
                        wSaleUtils.updateCartNavBar(data);
                    }
                    self.$el.trigger('dr_close_dialog', {});
                    return self._handleCartConfirmation(self.dr_cart_flow, data);
                }
            });
        },

        _isDefaultCartFLow: function () {
            return !_.contains(['side_cart', 'dialog', 'notification'], this.dr_cart_flow);
        },

        // Add product automatically
        // Or show not enough stock error
        _onChangeCombination: function () {
            this._super.apply(this, arguments);
            if (this.$el.hasClass('auto-add-product') && this.$('#add_to_cart').hasClass('out_of_stock')) {
                return this.displayNotification({
                    type: 'danger',
                    title: _t('No quantity available'),
                    message: _t('Can not add product in cart. No quantity available.'),
                    sticky: false,
                });
            } else if (this.$el.hasClass('auto-add-product')) {
                this.$('#add_to_cart').click();
            }
        },

        _onModalSubmit: function () {
            this.$el.trigger('dr_close_dialog', {});
            this._super.apply(this, arguments);
        }
    }));

});

odoo.define('theme_prime.cart_confirmation_dialog', function (require) {
'use strict';

    var Dialog = require('web.Dialog');

    return Dialog.extend({
        xmlDependencies: Dialog.prototype.xmlDependencies.concat(['/theme_prime/static/src/xml/core/cart_confirmation_dialog.xml', '/theme_prime/static/src/xml/frontend/2_col_deal.xml']),
        template: 'theme_prime.cart_confirmation_dialog',
        events: _.extend({}, Dialog.prototype.events, {
            'dr_close_dialog': 'close',
            'click .s_d_product_small_block .card': '_onClickProduct'
        }),
        /**
         * @constructor
         */
        init: function (parent, options) {
            this.data = options.data;
            if (this.data.accessory_product_ids.length) {
                this.data.accessory_product_ids_str = JSON.stringify(this.data.accessory_product_ids);
            }
            this._super(parent, _.extend({renderHeader: false, renderFooter: false, technical: false, size: options.size, backdrop: true}, options || {}));
        },
        /**
         * @override
         */
        start: function () {
            var sup = this._super.apply(this, arguments);
            // Append close button to dialog
            $('<button/>', {
                class: 'close',
                'data-dismiss': "modal",
                html: '<i class="fa fa-times"/>',
            }).prependTo(this.$modal.find('.modal-content'));
            this.$modal.find('.modal-dialog').addClass('modal-dialog-centered dr_full_dialog d_cart_confirmation_dialog');
            if (this.mini) {
                this.$modal.find('.modal-dialog').addClass('is_mini');
            }
            this.trigger_up('widgets_start_request', {
                $target: this.$('.s_d_product_small_block'),
            });
            return sup;
        },

        // TODO: fix this hack
        _onClickProduct: function (ev) {
            window.location.href = $(ev.currentTarget).find('.d-product-name a')[0].href;
        },
    });

});
