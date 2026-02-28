export default function StatCard({ icon, label, value, sub, color = 'blue' }) {
    return (
        <div className={`stat-card ${color}`}>
            <div className="stat-header">
                <div className="stat-icon">{icon}</div>
            </div>
            <div className="stat-label">{label}</div>
            <div className="stat-value">{value}</div>
            {sub && <div className="stat-sub">{sub}</div>}
        </div>
    );
}
