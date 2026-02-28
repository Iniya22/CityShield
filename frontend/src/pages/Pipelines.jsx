import { useEffect, useState } from 'react';
import { api, getUser } from '../services/api';
import Modal from '../components/Modal';

const emptyForm = {
    name: '', zone: '', material: 'PVC', diameter_mm: '',
    length_km: '', status: 'active', installed_date: '', last_inspection: ''
};

export default function Pipelines() {
    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({ ...emptyForm });
    const user = getUser();
    const canEdit = ['admin', 'operator'].includes(user?.role);

    const load = () => {
        setLoading(true);
        api.get('/api/pipelines').then(setRows).catch(console.error).finally(() => setLoading(false));
    };

    useEffect(load, []);

    const openAdd = () => { setEditing(null); setForm({ ...emptyForm }); setShowModal(true); };
    const openEdit = (row) => { setEditing(row); setForm({ ...row }); setShowModal(true); };

    const handleSave = async () => {
        try {
            if (editing) {
                await api.put(`/api/pipelines/${editing.id}`, form);
            } else {
                await api.post('/api/pipelines', form);
            }
            setShowModal(false);
            load();
        } catch (e) { alert(e.message); }
    };

    const handleDelete = async (id) => {
        if (!confirm('Delete this pipeline?')) return;
        try { await api.del(`/api/pipelines/${id}`); load(); }
        catch (e) { alert(e.message); }
    };

    const set = (key, val) => setForm({ ...form, [key]: val });

    return (
        <div className="page-enter">
            <div className="page-header">
                <h2>Pipelines</h2>
                <p>Manage water supply pipeline infrastructure</p>
            </div>

            <div className="table-card">
                <div className="table-header">
                    <h3>All Pipelines ({rows.length})</h3>
                    {canEdit && (
                        <button className="btn btn-primary btn-sm" onClick={openAdd}>+ Add Pipeline</button>
                    )}
                </div>

                {loading ? (
                    <div className="loading"><div className="spinner" /> Loading…</div>
                ) : rows.length === 0 ? (
                    <div className="empty-state"><div className="empty-icon">🔧</div><p>No pipelines found</p></div>
                ) : (
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Name</th><th>Zone</th><th>Material</th>
                                    <th>Diameter</th><th>Length</th><th>Status</th>
                                    <th>Installed</th>
                                    {canEdit && <th>Actions</th>}
                                </tr>
                            </thead>
                            <tbody>
                                {rows.map(r => (
                                    <tr key={r.id}>
                                        <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{r.name}</td>
                                        <td>{r.zone}</td>
                                        <td>{r.material}</td>
                                        <td>{r.diameter_mm} mm</td>
                                        <td>{r.length_km} km</td>
                                        <td><span className={`badge ${r.status}`}>{r.status}</span></td>
                                        <td>{r.installed_date || '—'}</td>
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
                    title={editing ? 'Edit Pipeline' : 'Add Pipeline'}
                    onClose={() => setShowModal(false)}
                    footer={
                        <>
                            <button className="btn btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
                            <button className="btn btn-primary" onClick={handleSave}>
                                {editing ? 'Update' : 'Create'}
                            </button>
                        </>
                    }
                >
                    <div className="form-row">
                        <div className="form-group">
                            <label>Name</label>
                            <input value={form.name} onChange={(e) => set('name', e.target.value)} placeholder="Pipeline name" />
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
                            <label>Material</label>
                            <select value={form.material} onChange={(e) => set('material', e.target.value)}>
                                {['PVC', 'HDPE', 'Cast Iron', 'Ductile Iron', 'Steel'].map(m => <option key={m}>{m}</option>)}
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
                            <label>Diameter (mm)</label>
                            <input type="number" value={form.diameter_mm} onChange={(e) => set('diameter_mm', +e.target.value)} />
                        </div>
                        <div className="form-group">
                            <label>Length (km)</label>
                            <input type="number" step="0.1" value={form.length_km} onChange={(e) => set('length_km', +e.target.value)} />
                        </div>
                    </div>
                    <div className="form-row">
                        <div className="form-group">
                            <label>Installed Date</label>
                            <input type="date" value={form.installed_date} onChange={(e) => set('installed_date', e.target.value)} />
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
