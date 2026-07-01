import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getConsultation, submitPhysicianReview } from '../services/api';

export default function PhysicianReview() {
  const navigate = useNavigate();
  const threadId = localStorage.getItem('threadId') || '';
  const [consultation, setConsultation] = useState(null);
  const [form, setForm] = useState({
    modified_recommendation: '',
    physician_treatment: '',
    physician_notes: '',
    reviewer_id: 'DR-001',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (threadId) {
      getConsultation(threadId).then(r => setConsultation(r.data)).catch(() => {});
    }
  }, [threadId]);

  const handleReview = async (approved) => {
    setLoading(true);
    try {
      const response = await submitPhysicianReview({
        thread_id: threadId,
        approved,
        ...form,
      });
      setConsultation(response.data);
      if (approved && response.data.consultation_status === 'completed') {
        navigate('/reports');
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Review submission failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Physician Review</h2>
        <p>Human-in-the-Loop review of Clinical Summary and Intermediate Recommendation</p>
      </div>

      {!threadId && <div className="alert alert-warning">No active consultation session.</div>}

      {consultation && (
        <>
          <div className="card">
            <h3>Clinical Summary</h3>
            <div className="report-section">
              <pre style={{ whiteSpace: 'pre-wrap' }}>{consultation.clinical_summary || 'Not yet generated'}</pre>
            </div>
          </div>

          <div className="card">
            <h3>Intermediate Recommendation</h3>
            <div className="report-section">
              <pre style={{ whiteSpace: 'pre-wrap' }}>{consultation.intermediate_recommendation || 'Not yet generated'}</pre>
            </div>
          </div>

          {consultation.possible_observations?.length > 0 && (
            <div className="card">
              <h3>Possible Observations</h3>
              <ul>{consultation.possible_observations.map((obs, i) => <li key={i}>{obs}</li>)}</ul>
            </div>
          )}

          <div className="card">
            <h3>Physician Actions</h3>
            <div className="form-group">
              <label>Modified Recommendation</label>
              <textarea name="modified_recommendation" value={form.modified_recommendation} onChange={(e) => setForm({...form, modified_recommendation: e.target.value})} placeholder="Override or modify the intermediate recommendation..." />
            </div>
            <div className="form-group">
              <label>Physician Treatment</label>
              <textarea name="physician_treatment" value={form.physician_treatment} onChange={(e) => setForm({...form, physician_treatment: e.target.value})} placeholder="Treatment notes..." />
            </div>
            <div className="form-group">
              <label>Physician Notes</label>
              <textarea name="physician_notes" value={form.physician_notes} onChange={(e) => setForm({...form, physician_notes: e.target.value})} placeholder="Additional review notes..." />
            </div>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button className="btn btn-success" onClick={() => handleReview(true)} disabled={loading}>
                Approve Report
              </button>
              <button className="btn btn-danger" onClick={() => handleReview(false)} disabled={loading}>
                Reject
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
