# FBR Connector Backend for Odoo 18

**Developed by ECOSIRE (PRIVATE) LIMITED**  
Website: https://www.ecosire.com/

## Overview

This module enables seamless integration between Odoo 18's backend invoicing and Pakistan's FBR (Federal Board of Revenue) system. It allows you to post invoices directly to FBR, print FBR-compliant receipts, and manage FBR compliance from within Odoo.

## Key Features
- Post invoice data to FBR directly from the invoice form or in bulk.
- Print FBR receipt showing the assigned invoice number and QR code.
- Support for adding service fees in FBR receipts.
- Dedicated "FBR" tab on the invoice form to display FBR response and invoice number.
- Enable or disable the FBR connector from configuration settings.
- Switch between Sandbox and Production modes for FBR authentication.
- Retry mechanism via scheduled cron job for failed FBR submissions.
- Manual option to resend failed FBR receipts from invoice view.
- Logging system to track successful and failed FBR submissions.
- Mass action in invoice list view to post multiple invoices to FBR in one go.
- Support for PCT (Pakistan Customs Tariff) code on products.
- Journal entries created/updated upon successful FBR submission.
- Seamless integration with Odoo’s core invoicing system.
- No extra dependencies required.

## Installation
1. Copy the `odoo_fbr_connector` folder into your Odoo 18 `addons` directory.
2. Update the app list and install the module from Odoo Apps.

## Configuration
1. Go to **Settings > Companies > FBR Configuration**.
2. Enable FBR integration and enter your FBR credentials (Authorization, POSID, etc.).
3. Choose Sandbox or Production mode as needed.
4. Optionally set service fee and logo.

## Usage
- Open any customer invoice and use the **Post Data to FBR** button to send it to FBR.
- Print the FBR receipt using the **Print FBR Receipt** button.
- View FBR response, invoice number, and QR code in the FBR tab.
- Use the mass action in the invoice list to post multiple invoices to FBR.
- Failed submissions are retried automatically by the scheduled job.
- View all FBR logs under **Accounting > Configuration > FBR Logs**.
- Set PCT code on products for FBR compliance.

## Support
For support, customization, or queries, contact:

**ECOSIRE (PRIVATE) LIMITED**  
Website: https://www.ecosire.com/

---
*This module is compatible with Odoo 18 Community and Enterprise editions.* 