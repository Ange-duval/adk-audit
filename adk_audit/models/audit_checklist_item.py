# -*- coding: utf-8 -*-
from odoo import fields, models


class AuditChecklistItem(models.Model):
    _name = 'audit.checklist.item'
    _description = "Point à Auditer (Modèle de Checklist)"
    _order = 'audit_type, sequence, name'

    name = fields.Char(string="Document / Point à contrôler", required=True)
    description = fields.Text(string="Description / Critère")
    audit_type = fields.Selection([
        ('metier', "Audit Métier (Finance / Gestion)"),
        ('qhse', "Audit QHSE"),
    ], string="Type d'audit", required=True, default='metier')
    department_id = fields.Many2one('hr.department', string="Service concerné (optionnel)",
                                     help="Laisser vide pour appliquer ce point à tous les services.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
