/** @odoo-module */

import { Order } from 'point_of_sale.models';
import Registries from "point_of_sale.Registries";


const PosReceiptOrder = (Order) => class PosReceiptOrder extends Order {

    /**
     * Add additional information for our ticket, such as new coupons and loyalty point gains.
     *
     * @override
     */
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        const categoryTotals = {};
        const uomTotals = {};

        for (const line of this.get_orderlines()) {
            const product = line.get_product();
            const category = product.categ_id ? product.categ_id[1] : 'Uncategorized';
            const uom = product.uom_id ? product.uom_id[1] : 'Units';
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
    }
}

Registries.Model.extend(Order, PosReceiptOrder);