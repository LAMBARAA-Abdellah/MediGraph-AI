import { useEffect, useState } from 'react';
import { getReport, getPdfReport } from '../services/api';

export default function Reports() {
  const threadId = localStorage.getItem('threadId') || '';
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (threadId) fetchReport();
  }, [threadId]);

  const fetchReport = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await getReport(threadId);
      setReport(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Report not available');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Clinical Orientation Report</h2>
        <p>View and export the final Preliminary Clinical Orientation Report</p>
      </div>

      <div className="card">
        <div className="form-group">
          <label>Thread ID</label>
          <input value={threadId} onChange={(e) => localStorage.setItem('threadId', e.target.value)} />
        </div>
        <button className="btn btn-primary" onClick={fetchReport} disabled={loading}>
          {loading ? 'Loading...' : 'Load Report'}
        </button>
      </div>

      {error && <div className="alert alert-warning">{error}</div>}

      {report && (
        <>
          <div className="disclaimer">{report.disclaimer}</div>

          {report.pdf_path && (
            <a href={getPdfReport(threadId)} className="btn btn-success" target="_blank" rel="noreferrer" style={{ marginBottom: '1rem' }}>
              Export PDF
            </a>
          )}

          <div className="card">
            <h3>Patient Information</h3>
            <div className="report-section">
              {report.json_report?.patient_information && (
                <div>
                  <p><strong>Name:</strong> {report.json_report.patient_information.name}</p>
                  <p><strong>Age:</strong> {report.json_report.patient_information.age}</p>
                  <p><strong>Gender:</strong> {report.json_report.patient_information.gender}</p>
                  <p><strong>Chief Complaint:</strong> {report.json_report.patient_information.chief_complaint}</p>
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <h3>Questions & Answers</h3>
            {report.json_report?.patient_answers?.map((qa, i) => (
              <div key={i} className="qa-item">
                <strong>Q{qa.question_number}: {qa.question}</strong>
                <p>{qa.answer}</p>
              </div>
            ))}
          </div>

          <div className="card">
            <h3>Clinical Summary</h3>
            <pre style={{ whiteSpace: 'pre-wrap' }}>{report.json_report?.clinical_summary}</pre>
          </div>

          <div className="card">
            <h3>Intermediate Recommendation</h3>
            <pre style={{ whiteSpace: 'pre-wrap' }}>{report.json_report?.intermediate_recommendation}</pre>
          </div>

          {report.json_report?.physician_treatment && (
            <div className="card">
              <h3>Physician Treatment</h3>
              <pre style={{ whiteSpace: 'pre-wrap' }}>{report.json_report.physician_treatment}</pre>
            </div>
          )}

          <div className="card">
            <h3>Markdown Report</h3>
            <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem', maxHeight: '400px', overflow: 'auto' }}>
              {report.markdown_report}
            </pre>
          </div>
        </>
      )}
    </div>
  );
}
