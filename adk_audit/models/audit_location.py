# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AuditLocation(models.Model):
    _name = 'audit.location'
    _description = "Localisation / Site Audité"
    _order = 'name'

    name = fields.Char(string="Site / Zone", required=True)
    company_id = fields.Many2one('res.company', string="Entreprise",
                                  default=lambda self: self.env.company, required=True)
    address = fields.Char(string="Adresse")
    department_id = fields.Many2one('hr.department', string="Service rattaché")
    responsible_id = fields.Many2one('hr.employee', string="Responsable du site")
    personnel_ids = fields.Many2many('hr.employee', 'audit_location_employee_rel',
                                      'location_id', 'employee_id',
                                      string="Personnel affecté au site")
    personnel_count = fields.Integer(compute='_compute_personnel_count', string="Effectif")
    notes = fields.Text(string="Notes")
    active = fields.Boolean(default=True)

    def _compute_personnel_count(self):
        for rec in self:
            rec.personnel_count = len(rec.personnel_ids)

    @api.onchange('department_id')
    def _onchange_department_id(self):
        if self.department_id and self.department_id.manager_id and not self.responsible_id:
            self.responsible_id = self.department_id.manager_id

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)',
         "Ce site existe déjà pour cette entreprise."),
    ]
