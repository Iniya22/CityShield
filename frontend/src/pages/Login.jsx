import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, setAuth } from '../services/api';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const data = await api.post('/api/auth/login', { username, password });
            setAuth(data.access_token, data.username, data.role);
            navigate('/dashboard');
        } catch (err) {
            setError(err.message || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-card">
                <div className="login-brand">
                    <div className="brand-shield">🏛️</div>
                    <h1>CityShield</h1>
                    <p>Urban Infrastructure Security Platform</p>
                </div>

                {error && <div className="login-error">{error}</div>}

                <form className="login-form" onSubmit={handleLogin}>
                    <div className="form-group">
                        <label>Username</label>
                        <input
                            type="text"
                            placeholder="Enter your username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            autoFocus
                        />
                    </div>
                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button className="btn btn-primary" type="submit" disabled={loading}>
                        {loading ? 'Authenticating…' : 'Sign In'}
                    </button>
                </form>

                <div className="login-demo">
                    <p>Demo credentials</p>
                    <p style={{ marginTop: 6 }}>
                        <code>admin / admin123</code> &nbsp;·&nbsp;
                        <code>operator1 / oper123</code> &nbsp;·&nbsp;
                        <code>viewer1 / view123</code>
                    </p>
                </div>
            </div>
        </div>
    );
}
