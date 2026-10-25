# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AuditAnomaly(models.Model):
    _name = 'audit.anomaly'
    _description = "Anomalie Détectée"
    _inherit = ['mail.thread']
    _order = 'severity desc, id desc'

    name = fields.Char(string="Résumé", required=True)
    description = fields.Text(string="Description")
    line_id = fields.Many2one('audit.line', string="Point d'audit lié",
                               ondelete='cascade')
    session_id = fields.Many2one('audit.session', string="Audit", required=True,
                                  ondelete='cascade', index=True)
    audit_type = fields.Selection(related='session_id.audit_type', store=True, readonly=True)
    location_id = fields.Many2one('audit.location', string="Localisation",
                                   related='session_id.location_id', store=True, readonly=False)
    department_id = fields.Many2one('hr.department', string="Service",
                                     related='session_id.department_id', store=True, readonly=False)

    severity = fields.Selection([
        ('low', "Faible"),
        ('medium', "Moyenne"),
        ('critical', "Critique"),
    ], string="Gravité", default='low', required=True, tracking=True)

    state = fields.Selection([
        ('open', "Ouverte"),
        ('in_progress', "En cours de traitement"),
        ('resolved', "Résolue"),
    ], string="Statut", default='open', tracking=True)

    image_ids = fields.One2many('audit.anomaly.image', 'anomaly_id', string="Photos / Preuves")
    image_count = fields.Integer(compute='_compute_image_count', string="Nb photos")
    thumbnail = fields.Binary(compute='_compute_thumbnail', string="Aperçu")

    responsible_id = fields.Many2one('res.users', string="Personne concernée", tracking=True)
    date_detected = fields.Date(string="Date de détection", default=fields.Date.context_today)

    action_ids = fields.One2many('audit.action', 'anomaly_id', string="Mesures prises")
    action_count = fields.Integer(compute='_compute_action_count')

    @api.depends('action_ids')
    def _compute_action_count(self):
        for rec in self:
            rec.action_count = len(rec.action_ids)

    @api.depends('image_ids')
    def _compute_image_count(self):
        for rec in self:
            rec.image_count = len(rec.image_ids)

    @api.depends('image_ids.image')
    def _compute_thumbnail(self):
        for rec in self:
            rec.thumbnail = rec.image_ids[:1].image if rec.image_ids else False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.line_id and rec.line_id.state == 'conforme':
                rec.line_id.state = 'non_conforme'
        return records

    def action_view_actions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Mesures prises",
            'res_model': 'audit.action',
            'view_mode': 'list,form',
            'domain': [('anomaly_id', '=', self.id)],
            'context': {'default_anomaly_id': self.id, 'default_session_id': self.session_id.id},
        }
