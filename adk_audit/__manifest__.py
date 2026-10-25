# -*- coding: utf-8 -*-
{
    'name': "ADK-AUDIT",
    'version': '18.0.1.1.0',
    'category': 'Services/Audit',
    'summary': "Audits métier et QHSE : checklists, anomalies avec preuves photo, plans d'actions, tableau de bord et rapport PDF - gratuit",
    'description': """
ADK-AUDIT
=========
Professional audit management for Odoo 18.

* Internal and external audit management.
* Business and QHSE audit workflows.
* Audit sessions, checklists, findings and action plans.
* Non-conformities and corrective actions.
* Role-based access for administrators, auditors and audited users.
* Dashboard for compliance, findings and deadlines.
* Professional PDF audit reports.
""",
    'author': "Kambeu Henang Ange Duval",
    'support': 'duvalkambeu61@gmail.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'hr', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/audit_location_views.xml',
        'views/audit_checklist_item_views.xml',
        'views/audit_department_views.xml',
        'views/audit_line_views.xml',
        'views/audit_anomaly_views.xml',
        'views/audit_action_views.xml',
        'views/audit_session_views.xml',
        'views/audit_dashboard_views.xml',
        'views/audit_dashboard_client.xml',
        'views/audit_menus.xml',
        'report/audit_report_templates.xml',
        'report/audit_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'adk_audit/static/src/scss/audit_dashboard.scss',
            'adk_audit/static/src/js/audit_dashboard.js',
            'adk_audit/static/src/xml/audit_dashboard.xml',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
