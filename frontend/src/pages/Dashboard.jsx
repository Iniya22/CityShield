import { useEffect, useState, useRef } from 'react';
import { api } from '../services/api';
import StatCard from '../components/StatCard';

export default function Dashboard() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const chartRef = useRef(null);
    const tankChartRef = useRef(null);

    useEffect(() => {
        api.get('/api/dashboard')
            .then(setStats)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    // Draw pipeline status chart
    useEffect(() => {
        if (!stats || !chartRef.current) return;
        drawStatusChart(chartRef.current, stats);
    }, [stats]);

    // Draw tank levels chart
    useEffect(() => {
        if (!stats || !tankChartRef.current) return;
        api.get('/api/tanks').then((tanks) => {
            drawTankChart(tankChartRef.current, tanks);
        });
    }, [stats]);

    if (loading) {
        return <div className="loading"><div className="spinner" /> Loading dashboard…</div>;
    }

    if (!stats) {
        return <div className="empty-state"><div className="empty-icon">⚠️</div><p>Failed to load dashboard data</p></div>;
    }

    return (
        <div className="page-enter">
            <div className="page-header">
                <h2>Dashboard</h2>
                <p>Urban Water Supply Department – Real-time Infrastructure Overview</p>
            </div>

            <div className="stats-grid">
                <StatCard icon="🔧" label="Total Pipelines" value={stats.total_pipelines}
                    sub={`${stats.active_pipelines} active`} color="blue" />
                <StatCard icon="💧" label="Water Tanks" value={stats.total_tanks}
                    sub={`${stats.active_tanks} active`} color="green" />
                <StatCard icon="⚠️" label="Critical Assets" value={stats.critical_assets}
                    sub="Requires attention" color="amber" />
                <StatCard icon="🛠️" label="Open Maintenance" value={stats.open_maintenance}
                    sub="Pending tasks" color="violet" />
            </div>

            <div className="charts-grid">
                <div className="chart-card">
                    <h3>Infrastructure Status Distribution</h3>
                    <div className="chart-container">
                        <canvas ref={chartRef} />
                    </div>
                </div>
                <div className="chart-card">
                    <h3>Tank Water Levels</h3>
                    <div className="chart-container">
                        <canvas ref={tankChartRef} />
                    </div>
                </div>
            </div>

            <div className="stats-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
                <div className="stat-card blue">
                    <div className="stat-label">Avg Tank Level</div>
                    <div className="stat-value">{stats.avg_tank_level}%</div>
                    <div className="stat-sub">Across all active tanks</div>
                </div>
                <div className="stat-card violet">
                    <div className="stat-label">Audit Events</div>
                    <div className="stat-value">{stats.recent_audit_events}</div>
                    <div className="stat-sub">Total security log entries</div>
                </div>
            </div>
        </div>
    );
}

/* ── Canvas chart helpers ─────────────────────────────────────────────────── */

function drawStatusChart(canvas, stats) {
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    ctx.scale(dpr, dpr);

    const w = rect.width, h = rect.height;
    const data = [
        { label: 'Active', value: stats.active_pipelines + stats.active_tanks, color: '#10b981' },
        { label: 'Critical', value: stats.critical_assets, color: '#f43f5e' },
        { label: 'Maintenance', value: stats.open_maintenance, color: '#f59e0b' },
        { label: 'Inactive', value: Math.max(0, stats.total_pipelines + stats.total_tanks - stats.active_pipelines - stats.active_tanks - stats.critical_assets), color: '#64748b' },
    ].filter(d => d.value > 0);

    const total = data.reduce((s, d) => s + d.value, 0) || 1;
    const cx = w * 0.35, cy = h / 2, r = Math.min(cx, cy) - 20;

    // Donut chart
    let angle = -Math.PI / 2;
    data.forEach(d => {
        const slice = (d.value / total) * Math.PI * 2;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, r, angle, angle + slice);
        ctx.fillStyle = d.color;
        ctx.fill();
        angle += slice;
    });

    // Center hole
    ctx.beginPath();
    ctx.arc(cx, cy, r * 0.55, 0, Math.PI * 2);
    ctx.fillStyle = '#111827';
    ctx.fill();

    // Center text
    ctx.fillStyle = '#f1f5f9';
    ctx.font = 'bold 24px Inter';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(total, cx, cy - 8);
    ctx.font = '11px Inter';
    ctx.fillStyle = '#94a3b8';
    ctx.fillText('Total Assets', cx, cy + 14);

    // Legend
    let ly = 30;
    ctx.textAlign = 'left';
    data.forEach(d => {
        ctx.fillStyle = d.color;
        ctx.beginPath();
        ctx.arc(w * 0.72, ly, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#94a3b8';
        ctx.font = '12px Inter';
        ctx.fillText(`${d.label} (${d.value})`, w * 0.72 + 14, ly + 4);
        ly += 28;
    });
}

function drawTankChart(canvas, tanks) {
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    ctx.scale(dpr, dpr);

    const w = rect.width, h = rect.height;
    const barW = Math.min(50, (w - 60) / tanks.length - 12);
    const maxH = h - 70;
    const startX = 40;

    // Y-axis
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.fillStyle = '#64748b';
    ctx.font = '10px Inter';
    ctx.textAlign = 'right';
    for (let pct = 0; pct <= 100; pct += 25) {
        const y = h - 40 - (pct / 100) * maxH;
        ctx.beginPath();
        ctx.moveTo(startX, y);
        ctx.lineTo(w - 10, y);
        ctx.stroke();
        ctx.fillText(pct + '%', startX - 6, y + 3);
    }

    // Bars
    tanks.forEach((tank, i) => {
        const x = startX + 16 + i * (barW + 12);
        const barH = (tank.current_level_pct / 100) * maxH;
        const y = h - 40 - barH;

        // Bar gradient
        const grad = ctx.createLinearGradient(x, y, x, h - 40);
        if (tank.current_level_pct > 60) {
            grad.addColorStop(0, '#10b981');
            grad.addColorStop(1, '#06b6d4');
        } else if (tank.current_level_pct > 30) {
            grad.addColorStop(0, '#f59e0b');
            grad.addColorStop(1, '#10b981');
        } else {
            grad.addColorStop(0, '#f43f5e');
            grad.addColorStop(1, '#f59e0b');
        }

        // Rounded top bar
        const r = Math.min(4, barW / 2);
        ctx.beginPath();
        ctx.moveTo(x, h - 40);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.lineTo(x + barW - r, y);
        ctx.quadraticCurveTo(x + barW, y, x + barW, y + r);
        ctx.lineTo(x + barW, h - 40);
        ctx.fillStyle = grad;
        ctx.fill();

        // Percentage label
        ctx.fillStyle = '#f1f5f9';
        ctx.font = 'bold 10px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(tank.current_level_pct + '%', x + barW / 2, y - 6);

        // Tank name
        ctx.fillStyle = '#64748b';
        ctx.font = '9px Inter';
        ctx.save();
        ctx.translate(x + barW / 2, h - 24);
        ctx.rotate(-0.4);
        ctx.fillText(tank.name.replace('Tank-', ''), 0, 0);
        ctx.restore();
    });
}
