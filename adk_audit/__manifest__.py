# -*- coding: utf-8 -*-
{
    'name': "ADK-AUDIT",
    'version': '18.0.1.0.0',
    'category': 'Services/Audit',
    'summary': "Gestion des audits Métier et QHSE avec dashboard et rapports",
    'description': """
ADK-AUDIT
=========
Module de gestion des audits internes et externes.

* Segmentation stricte Audit Métier (Finance/Gestion) et Audit QHSE.
* Fiches d'audit, points de contrôle (checklist), anomalies, plans d'action.
* Droits d'accès par profil (Admin, Auditeur Métier, Agent QHSE, Audité).
* Dashboard intégré (taux de conformité, anomalies par gravité, suivi délais).
* Génération de rapport d'audit PDF professionnel.
""",
    'author': "ADK",
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
        'views/audit_menus.xml',
        'report/audit_report_templates.xml',
        'report/audit_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
