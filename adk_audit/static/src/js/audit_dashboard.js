/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

const SEVERITY_COLORS = { critical: "#ee9a9a", medium: "#f2c48c", low: "#9ccfb4" };
const ANOMALY_COLORS = { open: "#ee9a9a", in_progress: "#f2c48c", resolved: "#9ccfb4" };
const ACTION_COLORS = { todo: "#c9bfd6", in_progress: "#8ec1e6", done: "#9ccfb4" };

export class AdkAuditDashboard extends Component {
    static template = "adk_audit.Dashboard";
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            type: "all",
            period: "all",
            data: null,
        });
        this.types = [
            { key: "all", label: "Tous les audits" },
            { key: "metier", label: "Métier" },
            { key: "qhse", label: "QHSE" },
        ];
        this.periods = [
            { key: "30", label: "30 jours" },
            { key: "90", label: "3 mois" },
            { key: "365", label: "12 mois" },
            { key: "all", label: "Tout" },
        ];
        onWillStart(() => this.load());
    }

    async load() {
        this.state.loading = true;
        this.state.data = await this.orm.call("audit.dashboard", "get_data", [], {
            audit_type: this.state.type,
            period: this.state.period,
        });
        this.state.loading = false;
    }

    async setType(key) {
        this.state.type = key;
        await this.load();
    }

    async setPeriod(key) {
        this.state.period = key;
        await this.load();
    }

    // ---------- Graphiques ----------
    donut(items, colors) {
        const r = 54;
        const C = 2 * Math.PI * r;
        const total = items.reduce((s, i) => s + i.value, 0);
        let acc = 0;
        return items.map((i) => {
            const len = total ? (i.value / total) * C : 0;
            const seg = {
                ...i,
                color: colors[i.key],
                dash: `${Math.max(len - 2, 0)} ${C - Math.max(len - 2, 0)}`,
                offset: -acc,
                pct: total ? Math.round((i.value / total) * 100) : 0,
            };
            acc += len;
            return seg;
        });
    }

    get severityDonut() {
        return this.donut(this.state.data.severity, SEVERITY_COLORS);
    }
    get anomalyDonut() {
        return this.donut(this.state.data.anomaly_state, ANOMALY_COLORS);
    }
    get actionDonut() {
        return this.donut(this.state.data.action_state, ACTION_COLORS);
    }
    get severityTotal() {
        return this.state.data.severity.reduce((s, i) => s + i.value, 0);
    }
    get anomalyTotal() {
        return this.state.data.anomaly_state.reduce((s, i) => s + i.value, 0);
    }
    get actionTotal() {
        return this.state.data.action_state.reduce((s, i) => s + i.value, 0);
    }

    get ringDash() {
        const C = 2 * Math.PI * 54;
        const v = Math.min(Math.max(this.state.data.kpis.conformity, 0), 100);
        return `${(v / 100) * C} ${C}`;
    }

    // Courbe + barres d'évolution mensuelle
    get chart() {
        const W = 640, H = 230, padL = 36, padR = 16, padT = 26, padB = 34;
        const months = this.state.data.monthly;
        const maxA = Math.max(...months.map((m) => m.audits), 1);
        const step = (W - padL - padR) / months.length;
        const bw = Math.min(step * 0.5, 46);
        const ph = H - padT - padB;
        const bars = months.map((m, i) => {
            const h = (m.audits / maxA) * ph * 0.72;
            const x = padL + step * i + (step - bw) / 2;
            return { x, y: H - padB - h, w: bw, h, label: m.label, value: m.audits, cx: x + bw / 2 };
        });
        const pts = months.map((m, i) => ({
            x: padL + step * i + step / 2,
            y: padT + ph - (m.conformity / 100) * ph,
            v: m.conformity,
            has: m.audits > 0,
        }));
        const drawn = pts.filter((p) => p.has);
        return {
            W, H, padL, padB, bars, pts, drawn,
            line: drawn.map((p) => `${p.x},${p.y}`).join(" "),
            grid: [0, 50, 100].map((v) => ({ v, y: padT + ph - (v / 100) * ph })),
        };
    }

    barColor(rate) {
        if (rate >= 80) return "#9ccfb4";
        if (rate >= 60) return "#f2c48c";
        return "#ee9a9a";
    }

    initials(name) {
        return (name || "?").split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase();
    }

    // ---------- Navigation ----------
    _domain(extra = []) {
        const d = [...extra];
        if (this.state.type !== "all") {
            d.push(["audit_type", "=", this.state.type]);
        }
        return d;
    }
    openList(name, model, domain) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: model,
            views: [[false, "list"], [false, "form"]],
            domain: this._domain(domain),
        });
    }
    openRecord(model, id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            res_id: id,
            views: [[false, "form"]],
        });
    }
    openAudits(domain = [], name = "Audits") { this.openList(name, "audit.session", domain); }
    openAnomalies(domain = [], name = "Anomalies") { this.openList(name, "audit.anomaly", domain); }
    openActions(domain = [], name = "Actions / Mesures") { this.openList(name, "audit.action", domain); }
}

registry.category("actions").add("adk_audit.dashboard", AdkAuditDashboard);
