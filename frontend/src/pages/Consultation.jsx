import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { startConsultation, getConsultation } from '../services/api';

export default function Consultation() {
  const navigate = useNavigate();
  const [threadId, setThreadId] = useState(localStorage.getItem('threadId') || '');
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (threadId) {
      getConsultation(threadId).then(r => setStatus(r.data)).catch(() => {});
    }
  }, [threadId]);

  const handleStart = async () => {
    if (!threadId) return;
    setLoading(true);
    try {
      const response = await startConsultation(threadId);
      setStatus(response.data);
      navigate('/questionnaire');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to start consultation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Consultation</h2>
        <p>Start the diagnostic questionnaire workflow</p>
      </div>

      <div className="card">
        <div className="form-group">
          <label>Session ID (Thread ID)</label>
          <input
            value={threadId}
            onChange={(e) => { setThreadId(e.target.value); localStorage.setItem('threadId', e.target.value); }}
            placeholder="Enter or paste thread ID"
          />
        </div>

        {status && (
          <div className="alert alert-info">
            Status: <strong>{status.consultation_status}</strong>
            {status.patient_information && (
              <div style={{ marginTop: '0.5rem' }}>
                Patient: {status.patient_information.name} | Age: {status.patient_information.age}
              </div>
            )}
          </div>
        )}

        <button className="btn btn-primary" onClick={handleStart} disabled={!threadId || loading}>
          {loading ? 'Starting...' : 'Start Consultation'}
        </button>
      </div>
    </div>
  );
}
