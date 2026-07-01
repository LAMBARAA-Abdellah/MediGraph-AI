import { useState } from 'react';

export default function ConsultationHistory() {
  const [threadId, setThreadId] = useState(localStorage.getItem('threadId') || '');

  const history = JSON.parse(localStorage.getItem('consultationHistory') || '[]');

  return (
    <div>
      <div className="page-header">
        <h2>Consultation History</h2>
        <p>View past consultation sessions</p>
      </div>

      <div className="card">
        <div className="form-group">
          <label>Current Session ID</label>
          <input value={threadId} readOnly />
        </div>
      </div>

      {history.length === 0 ? (
        <div className="alert alert-info">
          No consultation history stored locally. Complete a consultation to see it here.
        </div>
      ) : (
        history.map((item, i) => (
          <div key={i} className="card">
            <strong>{item.patientName}</strong> - {item.date}
            <p>Thread: {item.threadId}</p>
            <p>Status: {item.status}</p>
          </div>
        ))
      )}
    </div>
  );
}
