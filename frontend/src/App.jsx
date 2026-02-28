import { useState } from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { getToken, getUser } from './services/api';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Pipelines from './pages/Pipelines';
import WaterTanks from './pages/WaterTanks';
import Maintenance from './pages/Maintenance';
import AuditLog from './pages/AuditLog';
import './index.css';

function ProtectedRoute({ children }) {
  const token = getToken();
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function AppLayout({ children }) {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={
          <ProtectedRoute><AppLayout><Dashboard /></AppLayout></ProtectedRoute>
        } />
        <Route path="/pipelines" element={
          <ProtectedRoute><AppLayout><Pipelines /></AppLayout></ProtectedRoute>
        } />
        <Route path="/tanks" element={
          <ProtectedRoute><AppLayout><WaterTanks /></AppLayout></ProtectedRoute>
        } />
        <Route path="/maintenance" element={
          <ProtectedRoute><AppLayout><Maintenance /></AppLayout></ProtectedRoute>
        } />
        <Route path="/audit" element={
          <ProtectedRoute><AppLayout><AuditLog /></AppLayout></ProtectedRoute>
        } />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </HashRouter>
  );
}
