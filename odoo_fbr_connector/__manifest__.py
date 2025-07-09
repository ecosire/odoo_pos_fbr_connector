{
    'name': 'FBR Connector Backend',
    'version': '18.0.1.0.0',
    'summary': 'Sync Odoo Invoices with FBR (Pakistan) - Backend Only',
    'description': '''
Post invoice data to FBR directly from the invoice form.
Print FBR receipt showing the assigned invoice number.
Support for adding service fees in FBR receipts.
Display FBR response and invoice number in a dedicated "FBR" tab on the invoice form.
Enable or disable the FBR connector from configuration settings.
Option to switch between Sandbox and Production modes for FBR authentication.
Retry mechanism via scheduled cron job for failed FBR submissions.
Manual option to resend failed FBR receipts from invoice view.
Logging system to track successful and failed FBR submissions.
Mass action in invoice list view to post multiple invoices to FBR in one go.
Simple installation with no extra dependencies required.
Support for PCT (Pakistan Customs Tariff) code.
Journal entries created/updated upon successful FBR submission.
Seamless integration with Odoo’s core invoicing system.
''',
    'author': 'Ecosire (PRIVATE) LIMITED',
    'website': 'https://www.ecosire.com/',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/res_config_settings_views.xml',
        'views/fbr_log_views.xml',
        'data/ir_cron_data.xml',
    ],
    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
        'static/description/Screen 1.png',
        'static/description/Screen 2.png',
        'static/description/Screen 3.png',
        'static/description/Screen 4.png',
        'static/description/Screen 5.png',
        'static/description/Screen 6.png',
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
} 