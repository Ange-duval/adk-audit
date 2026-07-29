# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AuditLine(models.Model):
    _name = 'audit.line'
    _description = "Point d'audit / Checklist"
    _order = 'sequence, id'

    session_id = fields.Many2one('audit.session', string="Audit", required=True,
                                  ondelete='cascade')
    audit_type = fields.Selection(related='session_id.audit_type', store=True, readonly=True)
    sequence = fields.Integer(default=10)
    template_id = fields.Many2one('audit.checklist.item', string="Point type (catalogue)",
                                   ondelete='set null')
    name = fields.Char(string="Document / Point contrôlé", required=True)
    description = fields.Text(string="Description / Critère")
    state = fields.Selection([
        ('conforme', "Conforme"),
        ('non_conforme', "Non-conforme"),
        ('na', "Non applicable"),
    ], string="Statut", default='conforme', required=True)
    anomaly_ids = fields.One2many('audit.anomaly', 'line_id', string="Anomalies liées")
    anomaly_count = fields.Integer(compute='_compute_anomaly_count')

    @api.depends('anomaly_ids')
    def _compute_anomaly_count(self):
        for rec in self:
            rec.anomaly_count = len(rec.anomaly_ids)

    @api.onchange('state')
    def _onchange_state(self):
        # Force non-conforme si une anomalie existe déjà
        if self.state == 'conforme' and self.anomaly_ids:
            self.state = 'non_conforme'

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.name = self.template_id.name
            self.description = self.template_id.description
