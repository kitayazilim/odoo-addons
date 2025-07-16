/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

patch(PosOrder.prototype, {
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(...arguments);

        const categoryTotals = {};
        const uomTotals = {};

        for (const line of this.get_orderlines()) {
            const product = line.get_product();
            const category = product.categ_id ? product.categ_id.name : 'Uncategorized';
            const uom = product.uom_id ? product.uom_id.name : 'Units';
            const quantity = line.get_quantity();

            if (!categoryTotals[category]) {
                categoryTotals[category] = 0;
            }
            categoryTotals[category] += quantity;

            if (!uomTotals[uom]) {
                uomTotals[uom] = 0;
            }
            uomTotals[uom] += quantity;
        }

        result.category_totals = Object.entries(categoryTotals).map(([name, quantity]) => ({
            name,
            quantity,
        }));

        result.uom_totals = Object.entries(uomTotals).map(([name, quantity]) => ({
            name,
            quantity,
        }));

        return result;
    },
});
