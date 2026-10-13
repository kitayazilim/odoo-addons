# PayTR Payment Provider for Odoo

## Overview
This module integrates PayTR payment gateway with Odoo, allowing customers to make payments using PayTR's iframe solution. PayTR is a popular payment gateway in Turkey that supports various payment methods including credit cards, debit cards, and installment options.

## Features
- Integration with PayTR iframe payment solution
- Support for credit card payments
- Support for installment options
- Support for Troy card system
- Automatic transaction status updates
- Test mode for development and testing

## Requirements
- Odoo 18.0
- A PayTR merchant account
- PayTR API credentials (Merchant ID, API Key, API Salt)

## Installation
1. Clone this repository to your Odoo addons directory:
   ```
   git clone https://github.com/kitayazilim/kita-odoo-apps /path/to/odoo/addons/payment_paytr_kt
   ```

2. Update your Odoo addons list:
   - Go to Apps menu
   - Click on "Update Apps List"
   - Search for "PayTR iFrame" and install the module

3. Alternatively, you can install the module via the Apps menu by uploading the ZIP file.

## Configuration
1. Go to **Invoicing/Accounting > Configuration > Payment Providers**
2. Create a new payment provider or edit the existing PayTR provider
3. Set the provider to PayTR
4. Enter your PayTR credentials:
   - Merchant ID (Mağaza Numarası)
   - API Key (Mağaza Api Key)
   - API Salt (Mağaza Api Salt)
5. Configure additional settings:
   - Single payment option (Tek çekim)
   - Maximum installment count (En fazla taksit sayısı)
   - Timeout limit (Aşımı süresi)
6. Set the provider to "Test Mode" for testing or "Enabled" for production

## Usage
Once configured, the PayTR payment option will appear on your website's checkout page. When customers select this payment method, they will be redirected to the PayTR iframe to complete their payment.

y  ## Support
For support, please contact Kıta Yazılım:
- Website: https://kitayazilim.com
- Email: info@kitayazilim.com

## License
This module is licensed under LGPL-3.
