import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getMetrics, healthCheck } from '../services/api';

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    healthCheck().then(r => setHealth(r.data)).catch(() => setHealth({ status: 'unavailable' }));
    getMetrics().then(r => setMetrics(r.data)).catch(() => {});
  }, []);

  return (
    <div>
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>MediGraph AI - Intelligent Multi-Agent Clinical Orientation System</p>
      </div>

      <div className="alert alert-info">
        Educational project only. This system provides Preliminary Clinical Orientation, not medical diagnosis.
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="value">{health?.status === 'healthy' ? 'Online' : 'Offline'}</div>
          <div className="label">System Status</div>
        </div>
        <div className="stat-card">
          <div className="value">{metrics?.total_consultations ?? 0}</div>
          <div className="label">Total Consultations</div>
        </div>
        <div className="stat-card">
          <div className="value">{metrics?.completed_consultations ?? 0}</div>
          <div className="label">Completed</div>
        </div>
        <div className="stat-card">
          <div className="value">{metrics?.pending_reviews ?? 0}</div>
          <div className="label">Pending Reviews</div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '2rem' }}>
        <h3>Quick Actions</h3>
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap' }}>
          <Link to="/register" className="btn btn-primary">Register Patient</Link>
          <Link to="/consultation" className="btn btn-outline">Start Consultation</Link>
          <Link to="/physician" className="btn btn-outline">Physician Review</Link>
        </div>
      </div>

      <div className="card">
        <h3>Workflow Overview</h3>
        <ol style={{ paddingLeft: '1.5rem', marginTop: '1rem' }}>
          <li>Register patient information</li>
          <li>Start consultation - Diagnostic Agent asks 5 questions</li>
          <li>Clinical Summary and Intermediate Recommendation generated</li>
          <li>Physician Review (Human-in-the-Loop)</li>
          <li>Report Agent generates final report (JSON, Markdown, HTML, PDF)</li>
        </ol>
      </div>
    </div>
  );
}
