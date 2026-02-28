import { useEffect, useState } from 'react';
import { api, getUser } from '../services/api';
import Modal from '../components/Modal';

const emptyForm = {
    asset_type: 'pipeline', asset_id: 1, asset_name: '',
    description: '', priority: 'medium', status: 'open', assigned_to: ''
};

export default function Maintenance() {
    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({ ...emptyForm });
    const [filter, setFilter] = useState('all');
    const user = getUser();
    const canEdit = ['admin', 'operator'].includes(user?.role);

    const load = () => {
        setLoading(true);
        api.get('/api/maintenance').then(setRows).catch(console.error).finally(() => setLoading(false));
    };

    useEffect(load, []);

    const openAdd = () => { setEditing(null); setForm({ ...emptyForm }); setShowModal(true); };
    const openEdit = (row) => { setEditing(row); setForm({ ...row }); setShowModal(true); };

    const handleSave = async () => {
        try {
            if (editing) await api.put(`/api/maintenance/${editing.id}`, form);
            else await api.post('/api/maintenance', form);
            setShowModal(false); load();
        } catch (e) { alert(e.message); }
    };

    const handleDelete = async (id) => {
        if (!confirm('Delete this log entry?')) return;
        try { await api.del(`/api/maintenance/${id}`); load(); }
        catch (e) { alert(e.message); }
    };

    const set = (k, v) => setForm({ ...form, [k]: v });

    const filtered = filter === 'all' ? rows : rows.filter(r => r.status === filter);

    const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '—';

    return (
        <div className="page-enter">
            <div className="page-header">
                <h2>Maintenance Logs</h2>
                <p>Track maintenance activities across infrastructure assets</p>
            </div>

            <div className="table-card">
                <div className="table-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <h3>Logs ({filtered.length})</h3>
                        <div style={{ display: 'flex', gap: 4 }}>
                            {['all', 'open', 'in_progress', 'resolved'].map(f => (
                                <button
                                    key={f}
                                    className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-ghost'}`}
                                    onClick={() => setFilter(f)}
                                    style={{ textTransform: 'capitalize' }}
                                >
                                    {f.replace('_', ' ')}
                                </button>
                            ))}
                        </div>
                    </div>
                    {canEdit && <button className="btn btn-primary btn-sm" onClick={openAdd}>+ New Log</button>}
                </div>

                {loading ? (
                    <div className="loading"><div className="spinner" /> Loading…</div>
                ) : filtered.length === 0 ? (
                    <div className="empty-state"><div className="empty-icon">🛠️</div><p>No maintenance logs found</p></div>
                ) : (
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Asset</th><th>Description</th><th>Priority</th>
                                    <th>Status</th><th>Assigned To</th><th>Created</th>
                                    <th>Resolved</th>
                                    {canEdit && <th>Actions</th>}
                                </tr>
                            </thead>
                            <tbody>
                                {filtered.map(r => (
                                    <tr key={r.id}>
                                        <td>
                                            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                                                {r.asset_name || `${r.asset_type} #${r.asset_id}`}
                                            </span>
                                            <br />
                                            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{r.asset_type}</span>
                                        </td>
                                        <td style={{ maxWidth: 280 }}>{r.description}</td>
                                        <td><span className={`badge ${r.priority}`}>{r.priority}</span></td>
                                        <td><span className={`badge ${r.status}`}>{r.status.replace('_', ' ')}</span></td>
                                        <td>{r.assigned_to || '—'}</td>
                                        <td>{formatDate(r.created_at)}</td>
                                        <td>{formatDate(r.resolved_at)}</td>
                                        {canEdit && (
                                            <td>
                                                <div className="actions-cell">
                                                    <button className="btn-icon" onClick={() => openEdit(r)} title="Edit">✏️</button>
                                                    {user?.role === 'admin' && (
                                                        <button className="btn-icon" onClick={() => handleDelete(r.id)} title="Delete">🗑️</button>
                                                    )}
                                                </div>
                                            </td>
                                        )}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {showModal && (
                <Modal
                    title={editing ? 'Edit Maintenance Log' : 'New Maintenance Log'}
                    onClose={() => setShowModal(false)}
                    footer={
                        <>
                            <button className="btn btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
                            <button className="btn btn-primary" onClick={handleSave}>{editing ? 'Update' : 'Create'}</button>
                        </>
                    }
                >
                    <div className="form-row">
                        <div className="form-group">
                            <label>Asset Type</label>
                            <select value={form.asset_type} onChange={(e) => set('asset_type', e.target.value)}>
                                <option value="pipeline">Pipeline</option>
                                <option value="tank">Tank</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Asset ID</label>
                            <input type="number" value={form.asset_id} onChange={(e) => set('asset_id', +e.target.value)} />
                        </div>
                    </div>
                    <div className="form-group">
                        <label>Asset Name</label>
                        <input value={form.asset_name} onChange={(e) => set('asset_name', e.target.value)} placeholder="e.g. Pipeline-North-001" />
                    </div>
                    <div className="form-group">
                        <label>Description</label>
                        <textarea rows="3" value={form.description} onChange={(e) => set('description', e.target.value)} placeholder="Describe the maintenance issue…" />
                    </div>
                    <div className="form-row">
                        <div className="form-group">
                            <label>Priority</label>
                            <select value={form.priority} onChange={(e) => set('priority', e.target.value)}>
                                {['low', 'medium', 'high', 'critical'].map(p => <option key={p}>{p}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Status</label>
                            <select value={form.status} onChange={(e) => set('status', e.target.value)}>
                                {['open', 'in_progress', 'resolved'].map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                            </select>
                        </div>
                    </div>
                    <div className="form-group">
                        <label>Assigned To</label>
                        <input value={form.assigned_to} onChange={(e) => set('assigned_to', e.target.value)} placeholder="Technician name" />
                    </div>
                </Modal>
            )}
        </div>
    );
}
