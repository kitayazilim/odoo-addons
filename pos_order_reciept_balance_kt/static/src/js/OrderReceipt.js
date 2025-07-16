/** @odoo-module */

import Registries from "point_of_sale.Registries";
import OrderReceipt from "point_of_sale.OrderReceipt";
const { onWillStart } = owl;  

const OrderReceiptBalance = OrderReceipt => class extends OrderReceipt {
    setup() {
        super.setup()
        onWillStart(this.onWillStart)
    }

    async onWillStart() {
        if (this.receipt.partner && this.receipt.partner.id) {            
            try {
                this.amount = await this.env.services.rpc({
                    model: 'pos.payment',
                    method: 'get_partner_balance',
                    kwargs: {'partner_id' : this.receipt.partner.id},
                },
                {
                    timeout: 5000,
                })
            } catch (error) {
                this.amount = undefined
            }    
        }

    } 

    get balance() {
        if (this.receipt.partner){
            return this.amount ? this.amount : '#'
        }
    }

    get partner_name() {
        if (this.receipt.partner){
            return `${this.receipt.partner.name}`
        }
    }
}

Registries.Component.extend(OrderReceipt, OrderReceiptBalance)
 