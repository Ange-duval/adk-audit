# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AuditAction(models.Model):
    _name = 'audit.action'
    _description = "Action / Mesure Corrective"
    _inherit = ['mail.thread']
    _order = 'deadline asc, id desc'

    name = fields.Char(string="Plan d'action", required=True)
    anomaly_id = fields.Many2one('audit.anomaly', string="Anomalie liée", ondelete='cascade')
    session_id = fields.Many2one('audit.session', string="Audit", required=True,
                                  ondelete='cascade', index=True)
    audit_type = fields.Selection(related='session_id.audit_type', store=True, readonly=True)

    responsible_id = fields.Many2one('res.users', string="Responsable de l'action",
                                      required=True, tracking=True)
    deadline = fields.Date(string="Date limite", tracking=True)
    date_done = fields.Date(string="Date de réalisation")

    state = fields.Selection([
        ('todo', "A faire"),
        ('in_progress', "En cours"),
        ('done', "Réalisée"),
    ], string="Statut", default='todo', tracking=True)

    is_late = fields.Boolean(string="En retard", compute='_compute_is_late', store=True)

    @api.depends('deadline', 'state')
    def _compute_is_late(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_late = bool(rec.deadline and rec.deadline < today and rec.state != 'done')

    def action_mark_done(self):
        self.write({'state': 'done', 'date_done': fields.Date.context_today(self)})
        for rec in self:
            if rec.anomaly_id and all(a.state == 'done' for a in rec.anomaly_id.action_ids):
                rec.anomaly_id.state = 'resolved'
