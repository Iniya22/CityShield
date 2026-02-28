import { useEffect, useState } from 'react';
import { api, getUser } from '../services/api';
import Modal from '../components/Modal';

const emptyForm = {
    name: '', zone: '', capacity_liters: '', current_level_pct: 0,
    status: 'active', tank_type: 'overhead', last_cleaned: '', last_inspection: ''
};

export default function WaterTanks() {
    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({ ...emptyForm });
    const user = getUser();
    const canEdit = ['admin', 'operator'].includes(user?.role);

    const load = () => {
        setLoading(true);
        api.get('/api/tanks').then(setRows).catch(console.error).finally(() => setLoading(false));
    };

    useEffect(load, []);

    const openAdd = () => { setEditing(null); setForm({ ...emptyForm }); setShowModal(true); };
    const openEdit = (row) => { setEditing(row); setForm({ ...row }); setShowModal(true); };

    const handleSave = async () => {
        try {
            if (editing) await api.put(`/api/tanks/${editing.id}`, form);
            else await api.post('/api/tanks', form);
            setShowModal(false); load();
        } catch (e) { alert(e.message); }
    };

    const handleDelete = async (id) => {
        if (!confirm('Delete this water tank?')) return;
        try { await api.del(`/api/tanks/${id}`); load(); }
        catch (e) { alert(e.message); }
    };

    const set = (k, v) => setForm({ ...form, [k]: v });

    const levelClass = (pct) => pct > 60 ? 'high' : pct > 30 ? 'mid' : 'low';

    const formatCapacity = (liters) => {
        if (liters >= 1000000) return (liters / 1000000).toFixed(1) + ' ML';
        if (liters >= 1000) return (liters / 1000).toFixed(0) + ' KL';
        return liters + ' L';
    };

    return (
        <div className="page-enter">
            <div className="page-header">
                <h2>Water Tanks</h2>
                <p>Monitor and manage water storage tanks across zones</p>
            </div>

            <div className="table-card">
                <div className="table-header">
                    <h3>All Tanks ({rows.length})</h3>
                    {canEdit && <button className="btn btn-primary btn-sm" onClick={openAdd}>+ Add Tank</button>}
                </div>

                {loading ? (
                    <div className="loading"><div className="spinner" /> Loading…</div>
                ) : rows.length === 0 ? (
                    <div className="empty-state"><div className="empty-icon">💧</div><p>No tanks found</p></div>
                ) : (
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Name</th><th>Zone</th><th>Type</th>
                                    <th>Capacity</th><th>Level</th><th>Status</th>
                                    <th>Last Inspection</th>
                                    {canEdit && <th>Actions</th>}
                                </tr>
                            </thead>
                            <tbody>
                                {rows.map(r => (
                                    <tr key={r.id}>
                                        <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{r.name}</td>
                                        <td>{r.zone}</td>
                                        <td style={{ textTransform: 'capitalize' }}>{r.tank_type}</td>
                                        <td>{formatCapacity(r.capacity_liters)}</td>
                                        <td>
                                            <div className="level-bar-container">
                                                <div className="level-bar">
                                                    <div
                                                        className={`level-bar-fill ${levelClass(r.current_level_pct)}`}
                                                        style={{ width: r.current_level_pct + '%' }}
                                                    />
                                                </div>
                                                <span className="level-value">{r.current_level_pct}%</span>
                                            </div>
                                        </td>
                                        <td><span className={`badge ${r.status}`}>{r.status}</span></td>
                                        <td>{r.last_inspection || '—'}</td>
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
                    title={editing ? 'Edit Tank' : 'Add Tank'}
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
                            <label>Name</label>
                            <input value={form.name} onChange={(e) => set('name', e.target.value)} placeholder="Tank name" />
                        </div>
                        <div className="form-group">
                            <label>Zone</label>
                            <select value={form.zone} onChange={(e) => set('zone', e.target.value)}>
                                <option value="">Select zone</option>
                                {['North', 'South', 'East', 'West', 'Central'].map(z => <option key={z}>{z}</option>)}
                            </select>
                        </div>
                    </div>
                    <div className="form-row">
                        <div className="form-group">
                            <label>Type</label>
                            <select value={form.tank_type} onChange={(e) => set('tank_type', e.target.value)}>
                                {['overhead', 'underground', 'ground-level'].map(t => <option key={t}>{t}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Status</label>
                            <select value={form.status} onChange={(e) => set('status', e.target.value)}>
                                {['active', 'inactive', 'maintenance', 'critical'].map(s => <option key={s}>{s}</option>)}
                            </select>
                        </div>
                    </div>
                    <div className="form-row">
                        <div className="form-group">
                            <label>Capacity (liters)</label>
                            <input type="number" value={form.capacity_liters} onChange={(e) => set('capacity_liters', +e.target.value)} />
                        </div>
                        <div className="form-group">
                            <label>Current Level (%)</label>
                            <input type="number" min="0" max="100" value={form.current_level_pct} onChange={(e) => set('current_level_pct', +e.target.value)} />
                        </div>
                    </div>
                    <div className="form-row">
                        <div className="form-group">
                            <label>Last Cleaned</label>
                            <input type="date" value={form.last_cleaned} onChange={(e) => set('last_cleaned', e.target.value)} />
                        </div>
                        <div className="form-group">
                            <label>Last Inspection</label>
                            <input type="date" value={form.last_inspection} onChange={(e) => set('last_inspection', e.target.value)} />
                        </div>
                    </div>
                </Modal>
            )}
        </div>
    );
}
