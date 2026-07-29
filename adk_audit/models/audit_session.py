# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AuditSession(models.Model):
    _name = 'audit.session'
    _description = "Fiche Audit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string="Référence", required=True, copy=False,
                        readonly=True, default=lambda self: 'Nouveau')
    title = fields.Char(string="Titre de l'audit", required=True, tracking=True)
    audit_type = fields.Selection([
        ('metier', "Audit Métier (Finance / Gestion)"),
        ('qhse', "Audit QHSE"),
    ], string="Type d'audit", required=True, default='metier', tracking=True)

    company_audited_id = fields.Many2one('res.partner', string="Entreprise Auditée",
                                          tracking=True)
    company_id = fields.Many2one('res.company', string="Société",
                                  default=lambda self: self.env.company, required=True)
    department_id = fields.Many2one('hr.department', string="Service Audité", tracking=True)
    location_id = fields.Many2one('audit.location', string="Localisation / Site")

    auditor_ids = fields.Many2many('res.users', 'audit_session_auditor_rel',
                                    'session_id', 'user_id', string="Auditeurs",
                                    default=lambda self: self.env.user)
    date = fields.Date(string="Date de l'audit", default=fields.Date.context_today,
                        tracking=True)
    date_start = fields.Datetime(string="Début")
    date_end = fields.Datetime(string="Fin")

    state = fields.Selection([
        ('draft', "Brouillon"),
        ('in_progress', "En cours"),
        ('closed', "Clôturé"),
    ], string="Statut", default='draft', tracking=True, copy=False)

    line_ids = fields.One2many('audit.line', 'session_id', string="Points d'audit")
    anomaly_ids = fields.One2many('audit.anomaly', 'session_id', string="Anomalies")
    action_ids = fields.One2many('audit.action', 'session_id', string="Actions / Mesures")

    line_count = fields.Integer(compute='_compute_counts', string="Nb points")
    anomaly_count = fields.Integer(compute='_compute_counts', string="Nb anomalies")
    anomaly_open_count = fields.Integer(compute='_compute_counts', string="Anomalies ouvertes")
    action_count = fields.Integer(compute='_compute_counts', string="Nb actions")
    action_late_count = fields.Integer(compute='_compute_counts', string="Actions en retard")

    conformity_rate = fields.Float(string="Taux de conformité (%)",
                                    compute='_compute_conformity_rate', store=True)

    notes = fields.Html(string="Notes / Synthèse")
    color = fields.Integer(string="Couleur")

    @api.depends('line_ids.state')
    def _compute_conformity_rate(self):
        for rec in self:
            applicable = rec.line_ids.filtered(lambda l: l.state != 'na')
            total = len(applicable)
            if total:
                conforme = len(applicable.filtered(lambda l: l.state == 'conforme'))
                rec.conformity_rate = (conforme / total) * 100.0
            else:
                rec.conformity_rate = 0.0

    def _compute_counts(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)
            rec.anomaly_count = len(rec.anomaly_ids)
            rec.anomaly_open_count = len(rec.anomaly_ids.filtered(lambda a: a.state != 'resolved'))
            rec.action_count = len(rec.action_ids)
            rec.action_late_count = len(rec.action_ids.filtered(lambda a: a.is_late))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                seq_code = 'audit.session.qhse' if vals.get('audit_type') == 'qhse' else 'audit.session.metier'
                vals['name'] = self.env['ir.sequence'].next_by_code(seq_code) or 'Nouveau'
        return super().create(vals_list)

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_close(self):
        self.write({'state': 'closed'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_print_report(self):
        self.ensure_one()
        return self.env.ref('adk_audit.action_report_audit_session').report_action(self)

    def action_load_checklist(self):
        self.ensure_one()
        domain = [('audit_type', '=', self.audit_type)]
        if self.department_id:
            domain += ['|', ('department_id', '=', False), ('department_id', '=', self.department_id.id)]
        else:
            domain += [('department_id', '=', False)]
        templates = self.env['audit.checklist.item'].search(domain)
        existing_names = self.line_ids.mapped('name')
        vals_list = [{
            'session_id': self.id,
            'template_id': tpl.id,
            'name': tpl.name,
            'description': tpl.description,
            'sequence': tpl.sequence,
        } for tpl in templates if tpl.name not in existing_names]
        if vals_list:
            self.env['audit.line'].create(vals_list)
        return True

    def action_view_anomalies(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Anomalies",
            'res_model': 'audit.anomaly',
            'view_mode': 'list,kanban,form',
            'domain': [('session_id', '=', self.id)],
            'context': {'default_session_id': self.id},
        }

    def action_view_actions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Actions / Mesures",
            'res_model': 'audit.action',
            'view_mode': 'list,kanban,form',
            'domain': [('session_id', '=', self.id)],
            'context': {'default_session_id': self.id},
        }
