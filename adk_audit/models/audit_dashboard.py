# -*- coding: utf-8 -*-
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

MONTHS_FR = ['Janv.', 'Févr.', 'Mars', 'Avr.', 'Mai', 'Juin',
             'Juil.', 'Août', 'Sept.', 'Oct.', 'Nov.', 'Déc.']


class AuditDashboard(models.AbstractModel):
    """Fournit les données du tableau de bord ADK-AUDIT.

    Toutes les recherches passent par l'ORM : les règles d'accès de chaque
    rôle (Métier / QHSE / Admin) s'appliquent donc automatiquement.
    """
    _name = 'audit.dashboard'
    _description = "Données du tableau de bord ADK-AUDIT"

    @api.model
    def _period_start(self, period, today):
        return {
            '30': today - timedelta(days=30),
            '90': today - timedelta(days=90),
            '365': today - timedelta(days=365),
        }.get(period)

    @api.model
    def get_data(self, audit_type='all', period='all'):
        today = fields.Date.context_today(self)
        Session = self.env['audit.session']
        Anomaly = self.env['audit.anomaly']
        Action = self.env['audit.action']

        s_dom, a_dom = [], []
        if audit_type in ('metier', 'qhse'):
            s_dom.append(('audit_type', '=', audit_type))
            a_dom.append(('audit_type', '=', audit_type))
        start = self._period_start(period, today)
        if start:
            s_dom.append(('date', '>=', start))
            a_dom.append(('session_id.date', '>=', start))

        sessions = Session.search(s_dom)
        anomalies = Anomaly.search(a_dom)
        actions = Action.search(a_dom)
        done_sessions = sessions.filtered(lambda s: s.state != 'draft')

        def avg(recs):
            return round(sum(recs.mapped('conformity_rate')) / len(recs), 1) if recs else 0.0

        # ---------------- Indicateurs principaux ----------------
        open_anoms = anomalies.filtered(lambda a: a.state != 'resolved')
        critical_open = open_anoms.filtered(lambda a: a.severity == 'critical')
        late_actions = actions.filtered('is_late')
        done_actions = actions.filtered(lambda a: a.state == 'done')
        kpis = {
            'sessions_total': len(sessions),
            'sessions_in_progress': len(sessions.filtered(lambda s: s.state == 'in_progress')),
            'sessions_closed': len(sessions.filtered(lambda s: s.state == 'closed')),
            'sessions_draft': len(sessions.filtered(lambda s: s.state == 'draft')),
            'conformity': avg(done_sessions),
            'lines_checked': sum(done_sessions.mapped('line_count')),
            'anomalies_total': len(anomalies),
            'anomalies_open': len(open_anoms),
            'anomalies_critical': len(critical_open),
            'actions_total': len(actions),
            'actions_done': len(done_actions),
            'actions_late': len(late_actions),
            'actions_rate': round(len(done_actions) / len(actions) * 100, 1) if actions else 0.0,
            'resolution_rate': round(
                len(anomalies.filtered(lambda a: a.state == 'resolved')) / len(anomalies) * 100, 1
            ) if anomalies else 0.0,
        }

        # ---------------- Répartitions ----------------
        severity = [
            {'key': 'critical', 'label': "Critique", 'value': len(anomalies.filtered(lambda a: a.severity == 'critical'))},
            {'key': 'medium', 'label': "Moyenne", 'value': len(anomalies.filtered(lambda a: a.severity == 'medium'))},
            {'key': 'low', 'label': "Faible", 'value': len(anomalies.filtered(lambda a: a.severity == 'low'))},
        ]
        anomaly_state = [
            {'key': 'open', 'label': "Ouvertes", 'value': len(anomalies.filtered(lambda a: a.state == 'open'))},
            {'key': 'in_progress', 'label': "En traitement", 'value': len(anomalies.filtered(lambda a: a.state == 'in_progress'))},
            {'key': 'resolved', 'label': "Résolues", 'value': len(anomalies.filtered(lambda a: a.state == 'resolved'))},
        ]
        action_state = [
            {'key': 'todo', 'label': "À faire", 'value': len(actions.filtered(lambda a: a.state == 'todo'))},
            {'key': 'in_progress', 'label': "En cours", 'value': len(actions.filtered(lambda a: a.state == 'in_progress'))},
            {'key': 'done', 'label': "Réalisées", 'value': len(done_actions)},
        ]
        line_state = {'conforme': 0, 'non_conforme': 0, 'na': 0}
        for line in done_sessions.mapped('line_ids'):
            line_state[line.state] += 1

        # ---------------- Conformité par service ----------------
        by_service = []
        for dept in done_sessions.mapped('department_id'):
            subset = done_sessions.filtered(lambda s: s.department_id == dept)
            by_service.append({'name': dept.name, 'rate': avg(subset), 'count': len(subset)})
        by_service.sort(key=lambda r: -r['rate'])

        # ---------------- Évolution sur 6 mois ----------------
        first = today.replace(day=1) - relativedelta(months=5)
        monthly = []
        for i in range(6):
            m0 = first + relativedelta(months=i)
            m1 = m0 + relativedelta(months=1)
            ms = sessions.filtered(lambda s: s.date and m0 <= s.date < m1)
            mdone = ms.filtered(lambda s: s.state != 'draft')
            monthly.append({
                'label': MONTHS_FR[m0.month - 1],
                'audits': len(ms),
                'conformity': avg(mdone),
                'anomalies': sum(ms.mapped('anomaly_count')),
            })

        # ---------------- Activité des auditeurs ----------------
        auditors = []
        for user in sessions.mapped('auditor_ids'):
            subset = sessions.filtered(lambda s: user in s.auditor_ids)
            sub_done = subset.filtered(lambda s: s.state != 'draft')
            auditors.append({
                'name': user.name,
                'audits': len(subset),
                'closed': len(subset.filtered(lambda s: s.state == 'closed')),
                'points': sum(sub_done.mapped('line_count')),
                'anomalies': sum(subset.mapped('anomaly_count')),
                'conformity': avg(sub_done),
            })
        auditors.sort(key=lambda r: (-r['audits'], r['name']))

        # ---------------- Listes de suivi ----------------
        in_progress = sessions.filtered(lambda s: s.state == 'in_progress').sorted('date', reverse=True)[:6]
        crit = critical_open.sorted('date_detected', reverse=True)[:6]
        urgent = actions.filtered(lambda a: a.state != 'done').sorted(
            lambda a: a.deadline or date.max)[:6]
        type_label = dict(Session._fields['audit_type'].selection)

        return {
            'today': today.strftime('%d/%m/%Y'),
            'kpis': kpis,
            'severity': severity,
            'anomaly_state': anomaly_state,
            'action_state': action_state,
            'line_state': line_state,
            'by_service': by_service,
            'monthly': monthly,
            'auditors': auditors,
            'in_progress': [{
                'id': s.id, 'name': s.name, 'title': s.title,
                'type': s.audit_type, 'type_label': type_label.get(s.audit_type),
                'department': s.department_id.name or '',
                'rate': round(s.conformity_rate, 1),
                'open': s.anomaly_open_count, 'late': s.action_late_count,
            } for s in in_progress],
            'critical': [{
                'id': a.id, 'name': a.name, 'audit': a.session_id.name,
                'who': a.responsible_id.name or '',
                'date': a.date_detected.strftime('%d/%m/%Y') if a.date_detected else '',
            } for a in crit],
            'urgent': [{
                'id': a.id, 'name': a.name, 'who': a.responsible_id.name or '',
                'deadline': a.deadline.strftime('%d/%m/%Y') if a.deadline else '',
                'late': a.is_late,
                'days': (a.deadline - today).days if a.deadline else None,
            } for a in urgent],
        }
