# -*- coding: utf-8 -*-
from odoo import fields, models


class AuditAnomalyImage(models.Model):
    _name = 'audit.anomaly.image'
    _description = "Photo / Preuve d'Anomalie"
    _order = 'sequence, id'

    anomaly_id = fields.Many2one('audit.anomaly', string="Anomalie", required=True,
                                  ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Légende", default="Photo")
    image = fields.Image(string="Photo", required=True, max_width=1920, max_height=1920)
