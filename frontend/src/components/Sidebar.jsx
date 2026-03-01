import { useNavigate, useLocation } from 'react-router-dom';
import { getUser, clearAuth } from '../services/api';

const navItems = [
    { path: '/dashboard', icon: '📊', label: 'Dashboard' },
    { path: '/pipelines', icon: '🔧', label: 'Pipelines' },
    { path: '/tanks', icon: '💧', label: 'Water Tanks' },
    { path: '/maintenance', icon: '🛠️', label: 'Maintenance' },
];

const adminItems = [
    { path: '/audit', icon: '🛡️', label: 'Audit Log' },
];

export default function Sidebar() {
    const navigate = useNavigate();
    const location = useLocation();
    const user = getUser();

    const handleLogout = () => {
        clearAuth();
        navigate('/login');
    };

    const isActive = (path) => location.pathname === path;

    return (
        <aside className="sidebar">
            <div className="sidebar-brand">
                <div className="brand-icon">🏛️</div>
                <div>
                    <h1>CityShield</h1>
                    <div className="brand-sub">Urban Security Platform</div>
                </div>
            </div>

            <nav className="sidebar-nav">
                <div className="nav-section-title">Infrastructure</div>
                {navItems.map((item) => (
                    <a
                        key={item.path}
                        className={`nav-item${isActive(item.path) ? ' active' : ''}`}
                        onClick={() => navigate(item.path)}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        {item.label}
                    </a>
                ))}

                {user?.role === 'admin' && (
                    <>
                        <div className="nav-section-title">Security</div>
                        {adminItems.map((item) => (
                            <a
                                key={item.path}
                                className={`nav-item${isActive(item.path) ? ' active' : ''}`}
                                onClick={() => navigate(item.path)}
                            >
                                <span className="nav-icon">{item.icon}</span>
                                {item.label}
                            </a>
                        ))}
                    </>
                )}
            </nav>

            <div className="sidebar-footer">
                <div className="user-card">
                    <div className="user-avatar">
                        {user?.username?.[0]?.toUpperCase() || '?'}
                    </div>
                    <div className="user-info">
                        <div className="user-name">{user?.username || 'Unknown'}</div>
                        <div className="user-role">{user?.role || 'N/A'}</div>
                    </div>
                    <button className="btn-logout" onClick={handleLogout} title="Logout">
                        ⏻
                    </button>
                </div>
            </div>
        </aside>
    );
}
