import { useEffect, useState } from 'react';
import { api, getUser } from '../services/api';

export default function AuditLog() {
    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(true);
    const user = getUser();

    useEffect(() => {
        api.get('/api/audit')
            .then(setRows)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (user?.role !== 'admin') {
        return (
            <div className="page-enter">
                <div className="empty-state">
                    <div className="empty-icon">🔒</div>
                    <p>Access denied. Admin role required.</p>
                </div>
            </div>
        );
    }

    const riskClass = (score) => score >= 0.5 ? 'risk-high' : score >= 0.2 ? 'risk-mid' : 'risk-low';

    const formatTime = (t) => t ? new Date(t).toLocaleString() : '—';

    const methodColor = (m) => {
        const map = { GET: '#10b981', POST: '#3b82f6', PUT: '#f59e0b', DELETE: '#f43f5e' };
        return map[m] || '#94a3b8';
    };

    return (
        <div className="page-enter">
            <div className="page-header">
                <h2>Audit Log</h2>
                <p>Security event trail — anomaly detection and access monitoring</p>
            </div>

            <div className="table-card">
                <div className="table-header">
                    <h3>Security Events ({rows.length})</h3>
                </div>

                {loading ? (
                    <div className="loading"><div className="spinner" /> Loading…</div>
                ) : rows.length === 0 ? (
                    <div className="empty-state"><div className="empty-icon">🛡️</div><p>No audit events yet</p></div>
                ) : (
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Timestamp</th><th>User</th><th>Method</th>
                                    <th>Resource</th><th>Detail</th><th>IP</th>
                                    <th>Risk</th>
                                </tr>
                            </thead>
                            <tbody>
                                {rows.map(r => (
                                    <tr key={r.id}>
                                        <td style={{ whiteSpace: 'nowrap', fontSize: 12 }}>{formatTime(r.timestamp)}</td>
                                        <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{r.user}</td>
                                        <td>
                                            <span style={{
                                                padding: '3px 8px',
                                                borderRadius: 4,
                                                fontSize: 11,
                                                fontWeight: 700,
                                                background: methodColor(r.action) + '18',
                                                color: methodColor(r.action),
                                                letterSpacing: 0.5
                                            }}>
                                                {r.action}
                                            </span>
                                        </td>
                                        <td style={{ fontFamily: 'monospace', fontSize: 12 }}>{r.resource}</td>
                                        <td style={{ fontSize: 12 }}>{r.detail || '—'}</td>
                                        <td style={{ fontFamily: 'monospace', fontSize: 12 }}>{r.ip_address || '—'}</td>
                                        <td>
                                            <span className={`risk-dot ${riskClass(r.risk_score)}`} />
                                            {r.risk_score.toFixed(2)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
