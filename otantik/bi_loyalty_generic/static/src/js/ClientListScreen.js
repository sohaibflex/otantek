odoo.define('bi_loyalty_generic.ClientListScreenWidget', function(require) {
	"use strict";

	const ClientListScreen = require('point_of_sale.ClientListScreen');
	const { debounce } = owl.utils;
	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const { useListener } = require('web.custom_hooks');


	const ClientListScreenWidget = (ClientListScreen) =>
		class extends ClientListScreen {
			constructor() {
				super(...arguments);
				var self = this;
				setInterval(function(){
					self.searchClient();
				}, 3000);
				this.searchClient()
			}

			async searchClient() {
				let result = await this.getNewClient();
				this.env.pos.db.add_partners(result);
				this.render();
			}

			async getNewClient() {
				var domain = [];
				if(this.state.query) {
					domain = [["name", "ilike", this.state.query + "%"]];
				}
				var fields = _.find(this.env.pos.models, function(model){ return model.label === 'load_partners'; }).fields;
				var result = await this.rpc({
					model: 'res.partner',
					method: 'search_read',
					args: [domain, fields],
					kwargs: {
						limit: 10,
					},
				},{
					timeout: 3000,
					shadow: true,
				});

				return result;
			}
	};

	Registries.Component.extend(ClientListScreen, ClientListScreenWidget);

	return ClientListScreen;
});
